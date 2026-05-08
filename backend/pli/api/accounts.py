"""Endpoints comptes mail connectes.

Sprint 1 . US-1.8 (consomme par le Drawer FE).

GET /accounts
    Liste les comptes OAuth actifs. Projection volontairement etroite
    (pas de tokens OAuth, pas de cursor d'historique) + unread_count agrege
    depuis la table contacts.

POST /accounts/{id}/sync
    Declenche une sync manuelle en tache de fond (Sprint 2+).

DELETE /accounts/{id}
    Soft-delete : is_active=0. Les messages restent consultables en lecture
    jusqu'a purge explicite (GDPR M3).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal, cast

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr

from ..db import get_conn
from ..sync import sync_account

router = APIRouter()


class AccountSummary(BaseModel):
    """Projection publique d'un compte pour le Drawer.

    Ne contient jamais les tokens OAuth ni le cursor d'historique.
    `last_sync_at` est un ISO UTC (ou null si jamais synchronise).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: Literal["gmail", "microsoft"]
    email: EmailStr
    display_name: str | None = None
    avatar_color: str | None = None
    unread_count: int = 0
    is_active: bool = True
    last_sync_at: datetime | None = None


def _row_to_summary(row: dict[str, Any]) -> AccountSummary:
    last_sync_epoch = row.get("last_sync_at")
    last_sync_iso = (
        datetime.fromtimestamp(int(last_sync_epoch), tz=UTC) if last_sync_epoch else None
    )
    return AccountSummary(
        id=row["id"],
        provider=row["provider"],
        email=row["email"],
        display_name=row.get("display_name"),
        avatar_color=row.get("avatar_color"),
        unread_count=int(row.get("unread_count") or 0),
        is_active=bool(row.get("is_active", 1)),
        last_sync_at=last_sync_iso,
    )


@router.get("", response_model=list[AccountSummary], summary="Lister les comptes actifs")
def list_accounts() -> list[AccountSummary]:
    """Retourne tous les comptes OAuth actifs avec compteur de non-lus.

    Le compteur est une agregation en SQL (evite un N+1). L'ordre est
    `created_at ASC` pour que l'UI soit stable entre sessions.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                a.id, a.provider, a.email, a.display_name, a.avatar_color,
                a.is_active, a.last_sync_at,
                COALESCE(SUM(c.unread_count), 0) AS unread_count
            FROM accounts a
            LEFT JOIN contacts c ON c.account_id = a.id
            WHERE a.is_active = 1
            GROUP BY a.id
            ORDER BY a.created_at ASC
            """
        ).fetchall()
    return [_row_to_summary(dict(r)) for r in rows]


@router.post("/{account_id}/sync", summary="Lancer une sync manuelle")
async def trigger_sync(
    account_id: str,
    kind: str = "incremental",
    bg: BackgroundTasks = None,  # type: ignore[assignment]
) -> dict[str, object]:
    if kind not in {"initial", "incremental"}:
        raise HTTPException(400, "kind invalide")
    sync_kind = cast(Literal["initial", "incremental"], kind)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM accounts WHERE id = ? AND is_active = 1", (account_id,)
        ).fetchone()
    if not row:
        raise HTTPException(404, "compte introuvable")
    if bg:
        bg.add_task(sync_account, account_id, sync_kind)
    return {"status": "started", "account_id": account_id, "kind": sync_kind}


@router.delete("/{account_id}", summary="Deconnecter un compte")
def remove_account(account_id: str) -> dict[str, str]:
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE accounts SET is_active = 0 WHERE id = ? AND is_active = 1",
            (account_id,),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "compte introuvable ou deja deconnecte")
    return {"status": "deactivated", "account_id": account_id}
