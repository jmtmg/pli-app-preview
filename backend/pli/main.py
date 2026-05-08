"""Entrypoint FastAPI - PLI backend.

Lance avec :
    uvicorn pli.main:app --reload --port 8000

En mode local, le port peut etre 0 (auto) : l'app remonte le port choisi sur
stdout, le frontend lit ce port depuis un fichier ou un flag.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .api import accounts, auth, contacts, conversations, demo, messages, search
from .config import settings
from .db import get_conn, healthcheck, init_db
from .logging_config import RequestLoggingMiddleware, configure_logging

configure_logging()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    log.info("pli_starting", version=__version__, mode=settings.mode)
    init_db()
    if settings.mode == "local" and settings.demo:
        from .demo import seed_demo_data

        demo_counts = seed_demo_data()
        log.info("pli_demo_seeded", **demo_counts)
    yield
    log.info("pli_stopping")


app = FastAPI(
    title="PLI API",
    version=__version__,
    description=f"Client mail conversationnel - mode {settings.mode}",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug or settings.mode == "local" else None,
)

# Middleware logging HTTP (doit etre avant CORS)
app.add_middleware(RequestLoggingMiddleware)

if settings.mode == "cloud":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# --- Health / root ---


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "PLI", "version": __version__, "mode": settings.mode}


@app.get("/health")
async def health() -> dict[str, object]:
    """Healthcheck complet : DB + comptes + last sync."""
    started = time.perf_counter()
    db_state = await healthcheck()

    accounts_stats: dict[str, object] = {"active": 0, "last_sync_at": None}
    try:
        if settings.mode == "local":
            with get_conn() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) AS n, MAX(last_sync_at) AS last "
                    "FROM accounts WHERE is_active = 1"
                ).fetchone()
                accounts_stats = {
                    "active": row["n"] or 0,
                    "last_sync_at": row["last"],
                }
    except Exception as e:  # pragma: no cover
        accounts_stats = {"error": str(e)[:100]}

    return {
        "status": "ok" if db_state.get("ok") else "degraded",
        "version": __version__,
        "mode": settings.mode,
        "db": db_state,
        "accounts": accounts_stats,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
    }


# --- Routers Sprint 1 (M1) ---
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(demo.router, prefix="/demo", tags=["demo-local"])


# --- Routers M2 (kill-switch PLI_ENABLE_M2, cf. ADR 0007) ---
# Par defaut off : Sprint 1 reste stable sans regression.
# En dev / CI : PLI_ENABLE_M2=1 active auth PLI + billing Stripe + licences.
if settings.enable_m2:
    from .api import auth_pli as auth_pli_router
    from .api import billing as billing_router
    from .api import licensing as licensing_router
    from .tenancy.context import TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
    # /auth cohabite : /auth/{provider}/start (M1 OAuth) + /auth/signup (M2).
    app.include_router(auth_pli_router.router, prefix="/auth", tags=["auth-pli"])
    app.include_router(billing_router.router, prefix="/billing", tags=["billing"])
    app.include_router(licensing_router.router, prefix="/licenses", tags=["licenses"])
    log.info("pli_m2_routers_enabled")
else:
    log.info("pli_m2_routers_disabled")
