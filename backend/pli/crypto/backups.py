"""
Pipeline backups chiffrés (PLI Cloud).

- `backup_database()` : pg_dump → gzip → age-encrypt → upload S3-compat.
- `run_restore_drill()` : télécharge un backup récent, déchiffre, restaure
  sur base jetable, vérifie quelques invariants, nettoie.

Threat Model doc 11 §5.2 — mitigation M-INFRA-04.
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pli.config import settings
from pli.storage import get_storage

log = logging.getLogger(__name__)

BACKUP_PREFIX = "backups/postgres/"
DRILL_SUFFIX = ".drill"


class BackupError(Exception):
    pass


@dataclass(frozen=True)
class BackupResult:
    key: str
    size_bytes: int
    duration_s: float
    sha256: str


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------


def backup_database() -> BackupResult:
    """Dump → compress → encrypt → upload. Raises BackupError on any failure."""
    started = time.perf_counter()
    now = datetime.now(UTC)
    name = f"pli-{now.strftime('%Y%m%dT%H%M%SZ')}.sql.gz.age"
    key = BACKUP_PREFIX + name

    with tempfile.TemporaryDirectory(prefix="pli-backup-") as tmp:
        path = Path(tmp) / name
        _run_encrypted_dump(path, age_recipient=settings.backup_age_recipient)
        size = path.stat().st_size
        sha = _sha256sum(path)
        with path.open("rb") as fh:
            get_storage().put(
                key,
                fh.read(),
                content_type="application/octet-stream",
                encrypt=False,  # already age-encrypted
            )

    duration = time.perf_counter() - started
    log.info(
        "backup ok key=%s size=%s duration=%.2fs sha256=%s",
        key,
        size,
        duration,
        sha,
    )
    _emit_metric("backup.duration_s", duration)
    _emit_metric("backup.size_bytes", size)
    return BackupResult(key=key, size_bytes=size, duration_s=duration, sha256=sha)


def _run_encrypted_dump(path: Path, *, age_recipient: str) -> None:
    """pg_dump | gzip | age > path"""
    if not age_recipient:
        raise BackupError("age recipient not configured (settings.backup_age_recipient)")

    # Use -Fc for custom format (smaller, parallelizable restore). Gzip to keep
    # age input deterministic & streaming-friendly.
    cmd_dump = [
        "pg_dump",
        "-Fc",
        "-Z",
        "9",
        settings.database_url,
    ]
    cmd_age = ["age", "-r", age_recipient, "-o", str(path)]

    log.info("running pg_dump | age → %s", path.name)
    dump = subprocess.Popen(cmd_dump, stdout=subprocess.PIPE)
    age = subprocess.Popen(cmd_age, stdin=dump.stdout)
    if dump.stdout:
        dump.stdout.close()  # Allow SIGPIPE from age to propagate.
    age_rc = age.wait()
    dump_rc = dump.wait()

    if dump_rc != 0:
        raise BackupError(f"pg_dump exited {dump_rc}")
    if age_rc != 0:
        raise BackupError(f"age exited {age_rc}")
    if path.stat().st_size < 1024:
        raise BackupError("encrypted backup suspiciously small")


# ---------------------------------------------------------------------------
# Restore drill
# ---------------------------------------------------------------------------


def run_restore_drill(key: str | None = None) -> None:
    """Download recent backup, decrypt, restore to ephemeral DB, check invariants."""
    storage = get_storage()
    if key is None:
        keys = storage.list(BACKUP_PREFIX, limit=5)
        if not keys:
            raise BackupError("no backup available for drill")
        key = sorted(keys, reverse=True)[0]

    log.info("drill: downloading %s", key)
    payload = storage.get(key)

    with tempfile.TemporaryDirectory(prefix="pli-drill-") as tmp:
        enc_path = Path(tmp) / "backup.age"
        dec_path = Path(tmp) / "backup.sql.gz"
        enc_path.write_bytes(payload)

        subprocess.check_call(
            [
                "age",
                "-d",
                "-i",
                settings.backup_age_identity_path,
                "-o",
                str(dec_path),
                str(enc_path),
            ]
        )

        drill_db = f"pli_drill_{int(time.time())}"
        subprocess.check_call(["createdb", drill_db])
        try:
            subprocess.check_call(
                [
                    "pg_restore",
                    "-d",
                    drill_db,
                    "--no-owner",
                    "--no-privileges",
                    "-j",
                    "2",
                    str(dec_path),
                ]
            )
            _verify_drill_invariants(drill_db)
        finally:
            subprocess.call(["dropdb", "--if-exists", drill_db])

    log.info("drill ok for %s", key)


def _verify_drill_invariants(dbname: str) -> None:
    """A few cheap sanity checks after restore."""
    probes = {
        "users_exists": "SELECT to_regclass('public.users') IS NOT NULL;",
        "messages_count_positive": "SELECT COUNT(*) > 0 FROM messages;",
        "rls_enabled_messages": ("SELECT relrowsecurity FROM pg_class WHERE relname = 'messages';"),
    }
    for name, sql in probes.items():
        result = subprocess.check_output(
            ["psql", "-d", dbname, "-tAc", sql],
            text=True,
        ).strip()
        if result.lower() not in ("t", "true", "1"):
            raise BackupError(f"drill invariant failed: {name} → {result!r}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256sum(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _emit_metric(name: str, value: float) -> None:
    try:
        from pli.observability import emit

        emit(name, value)
    except Exception:  # noqa: BLE001
        pass
