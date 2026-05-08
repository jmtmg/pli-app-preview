"""Endpoints de démonstration locale sans credentials réels."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..config import settings
from ..demo import seed_demo_data

router = APIRouter()


class DemoResetResponse(BaseModel):
    seeded: bool
    mode: str
    counts: dict[str, int]


def _ensure_local_mode() -> None:
    if settings.mode != "local":
        raise HTTPException(404, "démo locale indisponible hors mode local")


@router.post("/seed", summary="Seeder la démo locale")
def seed_demo(reset: bool = Query(False)) -> dict[str, int | bool]:
    """Seed local fictif plat, pratique pour scripts/smoke tests."""
    _ensure_local_mode()
    return seed_demo_data(reset=reset)


@router.post("/reset", response_model=DemoResetResponse, summary="Réinitialiser la démo locale")
def reset_local_demo() -> DemoResetResponse:
    """Reset + seed local fictif pour smoke backend/frontend sans OAuth ni secrets."""
    _ensure_local_mode()
    result = seed_demo_data(reset=True)
    counts = {
        "accounts": int(result["accounts"]),
        "contacts": int(result["contacts"]),
        "messages": int(result["messages"]),
        "attachments": int(result.get("attachments", 0)),
    }
    return DemoResetResponse(seeded=True, mode=settings.mode, counts=counts)
