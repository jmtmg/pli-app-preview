"""Adapters pour mode Local — machine de l'utilisateur, 1 tenant fixe."""

from __future__ import annotations

import hashlib
import os
from collections.abc import AsyncIterator
from pathlib import Path

# `tomllib` est stdlib depuis Python 3.11. Le paquet `tomli` offre la même
# API en fallback pour les sandboxes de dev en 3.10 (la CI tourne en 3.11+,
# cf. `pyproject.toml` `requires-python = ">=3.11"`).
try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover — Python 3.10 backfill
    import tomli as tomllib  # type: ignore[no-redef]

import tomli_w
from cryptography.fernet import Fernet

from ..config import settings
from .base import (
    CryptoAdapter,
    Principal,
    SearchAdapter,
    SettingsStore,
    StorageAdapter,
    StorageNotFound,
    StoredObject,
    TenantIsolationError,
)

LOCAL_TENANT_ID = "local"


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


class LocalStorageAdapter(StorageAdapter):
    """Stocke les PJ sur disque sous ~/.pli/att/<sha256[:2]>/<sha256>.

    Aucun chiffrement ici : le FS est supposé chiffré par SQLCipher + l'OS.
    Le `tenant_id` doit être LOCAL_TENANT_ID sinon erreur.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or settings.attachments_dir
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, sha256: str) -> Path:
        return self.root / sha256[:2] / sha256

    async def put(
        self,
        *,
        tenant_id: str,
        key: str,  # ignoré en local — on utilise sha256 comme clé
        data: bytes,
        content_type: str | None = None,
    ) -> StoredObject:
        if tenant_id != LOCAL_TENANT_ID:
            raise TenantIsolationError(f"Local adapter only accepts tenant_id='{LOCAL_TENANT_ID}'")
        sha = hashlib.sha256(data).hexdigest()
        dest = self._path(sha)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():  # dédup par contenu
            dest.write_bytes(data)
        return StoredObject(key=sha, size_bytes=len(data), content_type=content_type, sha256=sha)

    async def get(self, *, tenant_id: str, key: str) -> bytes:
        if tenant_id != LOCAL_TENANT_ID:
            raise TenantIsolationError("Local adapter")
        p = self._path(key)
        if not p.exists():
            raise StorageNotFound(key)
        return p.read_bytes()

    async def delete(self, *, tenant_id: str, key: str) -> None:
        if tenant_id != LOCAL_TENANT_ID:
            raise TenantIsolationError("Local adapter")
        p = self._path(key)
        p.unlink(missing_ok=True)

    async def presigned_url(self, *, tenant_id: str, key: str, ttl_seconds: int = 300) -> str:
        # En local, l'app sert les PJ via un endpoint signé court (HMAC du chemin)
        return f"/attachments/{key}?ttl={ttl_seconds}"

    async def iter_tenant(self, *, tenant_id: str) -> AsyncIterator[StoredObject]:
        if tenant_id != LOCAL_TENANT_ID:
            raise TenantIsolationError("Local adapter")
        for f in self.root.rglob("*"):
            if f.is_file():
                yield StoredObject(
                    key=f.name,
                    size_bytes=f.stat().st_size,
                    content_type=None,
                    sha256=f.name,
                )


# ---------------------------------------------------------------------------
# Search (FTS5)
# ---------------------------------------------------------------------------


class LocalSearchAdapter(SearchAdapter):
    """Utilise les triggers FTS5 du schéma SQLite : rien à faire côté adapter
    en écriture — les INSERT/UPDATE/DELETE sur `messages` propagent
    automatiquement. L'adapter ne fait que les requêtes lecture.
    """

    async def index_message(
        self, *, tenant_id: str, message_id: str, subject: str, body: str, from_: str
    ) -> None:
        # No-op : les triggers schema.sql le font.
        return None

    async def query(self, *, tenant_id: str, q: str, limit: int = 50) -> list[dict]:
        from ..db import get_conn

        with get_conn() as conn:
            rows = conn.execute(
                "SELECT m.id, m.subject, snippet(messages_fts, 1, '[', ']', '…', 10) AS snip "
                "FROM messages_fts JOIN messages m ON m.rowid = messages_fts.rowid "
                "WHERE messages_fts MATCH ? LIMIT ?",
                (q, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    async def delete_message(self, *, tenant_id: str, message_id: str) -> None:
        return None  # trigger FTS5 le fait


# ---------------------------------------------------------------------------
# Principal resolver
# ---------------------------------------------------------------------------


async def local_principal_resolver(request) -> Principal:  # type: ignore[no-untyped-def]
    """En local, le principal est fixe.

    Fix C (ticket `M1-regression-m2.md`, hotfix 2026-04-23) : plan codé en
    dur à `"free"`. L'import précédent `from ..billing.licenses import
    current_local_plan` pointait vers un symbole inexistant et cassait
    100 % des endpoints Sprint 1 dès que `PLI_ENABLE_M2=1` (chaque requête
    transitait par `TenantContextMiddleware` → resolver → ImportError →
    401 auth_failed).

    TODO Sprint 2/3 : brancher sur la licence locale signée Ed25519
    (`pli.licensing.local_key.load_license().plan`). Décision direction
    2026-04-22 : ne pas introduire un couplage `billing` → `licensing` avant
    le vrai refactor. Cf. `docs/adr/0007-feature-flag-m2.md` §Rollout.
    """
    return Principal(
        tenant_id=LOCAL_TENANT_ID,
        user_id=LOCAL_TENANT_ID,
        plan="free",
        email=None,
    )


# ---------------------------------------------------------------------------
# Settings store (fichier TOML local)
# ---------------------------------------------------------------------------


class LocalSettingsStore(SettingsStore):
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (settings.db_path.parent / "settings.toml")

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        with self.path.open("rb") as f:
            return tomllib.load(f)  # type: ignore[return-value]

    def _save(self, data: dict[str, dict[str, str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("wb") as f:
            tomli_w.dump(data, f)

    async def get(self, *, tenant_id: str, key: str) -> str | None:
        return self._load().get(tenant_id, {}).get(key)

    async def set(self, *, tenant_id: str, key: str, value: str) -> None:
        data = self._load()
        data.setdefault(tenant_id, {})[key] = value
        self._save(data)

    async def delete(self, *, tenant_id: str, key: str) -> None:
        data = self._load()
        if tenant_id in data and key in data[tenant_id]:
            del data[tenant_id][key]
            self._save(data)


# ---------------------------------------------------------------------------
# Crypto (clé locale stockée dans Keychain / DPAPI / fichier avec 0600)
# ---------------------------------------------------------------------------


class LocalCryptoAdapter(CryptoAdapter):
    """Chiffre les tokens OAuth sensibles avec Fernet.

    La clé maître vit dans `~/.pli/crypto.key` (permissions 0600), ou idéalement
    dans le Keychain / DPAPI (implémenté en M3).
    """

    def __init__(self) -> None:
        key_path = settings.db_path.parent / "crypto.key"
        if not key_path.exists():
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key_path.write_bytes(Fernet.generate_key())
            try:
                os.chmod(key_path, 0o600)
            except OSError:
                pass  # Windows
        self._fernet = Fernet(key_path.read_bytes())

    def encrypt(self, plaintext: bytes) -> bytes:
        return self._fernet.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self._fernet.decrypt(ciphertext)
