"""Connexion DB — dialecte choisi par `settings.mode`.

Local : sqlite3 stdlib (+ SQLCipher si dispo).
Cloud : asyncpg pool partagé sur PostgreSQL, avec `set_local pli.current_tenant`
        injecté avant chaque requête (RLS).

Les modules métier doivent passer par :
- `get_conn()`  → SQLite synchrone (mode local)
- `get_pg_conn()` → PostgreSQL async (mode cloud), enveloppe d'asyncpg
"""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any

import structlog

from .config import settings

log = structlog.get_logger()
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


# ---------------------------------------------------------------------------
# SQLite (mode local)
# ---------------------------------------------------------------------------


def _connect_sqlite(db_path: Path, key: str | None = None) -> sqlite3.Connection:
    conn: sqlite3.Connection
    if key:
        try:
            from pysqlcipher3 import dbapi2 as sqlcipher

            conn = sqlcipher.connect(str(db_path))
            conn.execute(f"PRAGMA key = '{key}'")
        except ImportError:
            log.warning("sqlcipher_not_available_falling_back_plain_sqlite")
            conn = sqlite3.connect(str(db_path))
    else:
        conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db_local() -> None:
    """Crée la DB SQLite et applique le schéma. Pour le mode local uniquement."""
    settings.ensure_dirs()
    key = settings.sqlcipher_key.get_secret_value() if settings.sqlcipher_key else None
    with _connect_sqlite(settings.db_path, key) as conn:
        with SCHEMA_PATH.open() as f:
            conn.executescript(f.read())
        _migrate_local_schema(conn)
        conn.commit()
    log.info("db_initialized_sqlite", path=str(settings.db_path))


def _migrate_local_schema(conn: sqlite3.Connection) -> None:
    """Petites migrations idempotentes du MVP SQLite local.

    Le schéma est appliqué via `CREATE TABLE IF NOT EXISTS`; une base démo déjà
    créée ne reçoit donc pas automatiquement les nouvelles colonnes. On garde ici
    les ajouts non destructifs nécessaires aux features actives.
    """
    contact_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(contacts)").fetchall()
    }
    if "is_archived" not in contact_columns:
        conn.execute(
            "ALTER TABLE contacts ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0"
        )

    message_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(messages)").fetchall()
    }
    if "bcc_emails" not in message_columns:
        conn.execute("ALTER TABLE messages ADD COLUMN bcc_emails TEXT")

    # Brouillons locaux : l'invariant produit est un seul brouillon courant par
    # compte + conversation. Les anciennes DB démo peuvent avoir reçu plusieurs
    # lignes avant cette migration ; on conserve la plus récente avant de poser
    # l'index unique non destructif pour les démarrages suivants.
    conn.execute(
        """
        DELETE FROM drafts
        WHERE rowid NOT IN (
            SELECT keep_rowid FROM (
                SELECT d1.rowid AS keep_rowid
                FROM drafts d1
                WHERE d1.rowid = (
                    SELECT d2.rowid
                    FROM drafts d2
                    WHERE d2.account_id = d1.account_id
                      AND COALESCE(d2.contact_id, '') = COALESCE(d1.contact_id, '')
                    ORDER BY d2.updated_at DESC, d2.rowid DESC
                    LIMIT 1
                )
            )
        )
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_drafts_account_contact_unique
        ON drafts(account_id, COALESCE(contact_id, ''))
        """
    )


def init_db() -> None:
    """Dispatcher d'initialisation appelé au lifespan FastAPI.

    En mode cloud, le pool asyncpg est créé depuis un contexte async via
    `init_db_cloud()` — voir lifespan de `pli.main`. Cette fonction synchrone
    couvre le cas local, seul mode Sprint 1.
    """
    if settings.mode == "local":
        init_db_local()
    # En cloud, `init_db_cloud()` est appelé depuis le lifespan (contexte async).


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Connexion SQLite — mode local uniquement."""
    if settings.mode != "local":
        raise RuntimeError("get_conn() est réservé au mode local — utilise get_pg_conn()")
    key = settings.sqlcipher_key.get_secret_value() if settings.sqlcipher_key else None
    conn = _connect_sqlite(settings.db_path, key)
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# PostgreSQL (mode cloud) — pool asyncpg
# ---------------------------------------------------------------------------

_pg_pool: Any | None = None


async def init_db_cloud() -> None:
    """Crée le pool asyncpg. Les migrations Alembic doivent être exécutées
    indépendamment au déploiement (cf. scripts/migrate.sh)."""
    global _pg_pool
    if not settings.database_url:
        raise RuntimeError("PLI_DATABASE_URL manquant en mode cloud")
    import asyncpg

    _pg_pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    log.info("db_initialized_pg", dsn=settings.database_url.split("@")[-1])


async def close_db_cloud() -> None:
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None


@asynccontextmanager
async def get_pg_conn(tenant_id: str | None = None) -> AsyncIterator[Any]:
    """Connexion PG. Si `tenant_id` fourni, active la variable de session
    `pli.current_tenant` exploitée par les policies RLS."""
    if _pg_pool is None:
        raise RuntimeError("PG pool non initialisé — appelle init_db_cloud()")
    async with _pg_pool.acquire() as conn:
        if tenant_id:
            await conn.execute("SELECT set_config('pli.current_tenant', $1, true)", tenant_id)
        try:
            yield conn
        finally:
            if tenant_id:
                await conn.execute("RESET pli.current_tenant")


# ---------------------------------------------------------------------------
# Healthcheck commun
# ---------------------------------------------------------------------------


def healthcheck_local() -> dict[str, object]:
    try:
        with get_conn() as conn:
            row = conn.execute("SELECT count(*) AS n FROM accounts").fetchone()
        return {"ok": True, "accounts": row["n"]}
    except Exception as e:  # pragma: no cover
        return {"ok": False, "error": str(e)}


async def healthcheck_cloud() -> dict[str, object]:
    try:
        async with get_pg_conn() as conn:
            n = await conn.fetchval("SELECT count(*) FROM users")
        return {"ok": True, "users": n}
    except Exception as e:  # pragma: no cover
        return {"ok": False, "error": str(e)}


async def healthcheck() -> dict[str, object]:
    return await healthcheck_cloud() if settings.mode == "cloud" else healthcheck_local()
