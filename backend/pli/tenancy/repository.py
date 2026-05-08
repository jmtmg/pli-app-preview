"""Base class TenantScopedRepository (ADR-0002, couche 1).

Tous les repositories métier doivent en hériter. Ils reçoivent le tenant_id
au constructeur (depuis Depends(require_tenant)) et l'injectent dans toute
requête.
"""

from __future__ import annotations

import re
from typing import Any

from ..adapters.base import TenantIsolationError  # ré-exporté pour confort
from ..config import settings

# Patterns interdits qui révèlent un oubli de filtre tenant
_FORBIDDEN_PATTERNS = (
    re.compile(
        r"\bSELECT\s+.*\s+FROM\s+(accounts|messages|contacts|attachments|drafts)\b"
        r"(?![^;]*\bWHERE[^;]*\buser_id\b)",
        re.IGNORECASE | re.DOTALL,
    ),
)


class TenantScopedRepository:
    """Repository de base — accepte un tenant_id et expose helpers SQL.

    Les sous-classes appellent `self.execute(sql, ...)` qui :
    - vérifie que le SQL contient bien `user_id = :tenant`
    - injecte le param tenant_id automatiquement
    - exécute en local (sqlite3) ou cloud (asyncpg) selon settings.mode
    """

    def __init__(self, tenant_id: str) -> None:
        if not tenant_id:
            raise TenantIsolationError("tenant_id obligatoire")
        self.tenant_id = tenant_id

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _check_sql(sql: str) -> None:
        # Heuristique anti-oubli — non exhaustive mais détecte la majorité
        normalized = " ".join(sql.split())
        for pat in _FORBIDDEN_PATTERNS:
            if pat.search(normalized):
                raise TenantIsolationError(
                    f"SQL refusé : aucune clause user_id détectée — {sql[:120]}…"
                )

    async def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        self._check_sql(sql)
        params = {**(params or {}), "tenant_id": self.tenant_id}
        if settings.mode == "cloud":
            from ..db import get_pg_conn

            named_sql = sql  # asyncpg utilise $1, $2 — on convertit
            ordered_params: list[Any] = []
            for i, (k, v) in enumerate(params.items(), start=1):
                placeholder = f":{k}"
                if placeholder in named_sql:
                    named_sql = named_sql.replace(placeholder, f"${i}")
                    ordered_params.append(v)
            async with get_pg_conn(self.tenant_id) as conn:
                rows = await conn.fetch(named_sql, *ordered_params)
            return [dict(r) for r in rows]
        from ..db import get_conn

        with get_conn() as conn:
            cur = conn.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    async def fetch_one(self, sql: str, params: dict[str, Any] | None = None) -> dict | None:
        rows = await self.fetch_all(sql, params)
        return rows[0] if rows else None

    async def execute(self, sql: str, params: dict[str, Any] | None = None) -> None:
        # Pour INSERT/UPDATE/DELETE : on passe la même vérification.
        self._check_sql(sql)
        params = {**(params or {}), "tenant_id": self.tenant_id}
        if settings.mode == "cloud":
            from ..db import get_pg_conn

            named_sql = sql
            ordered_params: list[Any] = []
            for i, (k, v) in enumerate(params.items(), start=1):
                placeholder = f":{k}"
                if placeholder in named_sql:
                    named_sql = named_sql.replace(placeholder, f"${i}")
                    ordered_params.append(v)
            async with get_pg_conn(self.tenant_id) as conn:
                await conn.execute(named_sql, *ordered_params)
        else:
            from ..db import get_conn

            with get_conn() as conn:
                conn.execute(sql, params)
                conn.commit()
