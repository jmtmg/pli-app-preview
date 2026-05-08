"""Contexte tenant - middleware + ContextVar (ADR-0002, couche 2)."""

from __future__ import annotations

from contextvars import ContextVar

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

_current_tenant: ContextVar[str | None] = ContextVar("pli_tenant", default=None)

# Routes publiques qui ne demandent pas d'authentification.
PUBLIC_PATHS: set[str] = {
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/auth/signup",
    "/auth/login",
    "/auth/verify",
    "/auth/refresh",
    "/auth/password-reset/request",
    "/auth/password-reset/confirm",
    "/billing/webhook",
    "/billing/plans",
    "/pricing",
}


def current_tenant_id() -> str | None:
    return _current_tenant.get()


def require_tenant() -> str:
    tid = _current_tenant.get()
    if tid is None:
        raise HTTPException(status_code=401, detail="no_tenant_context")
    return tid


def set_current_tenant(tenant_id: str | None) -> None:
    _current_tenant.set(tenant_id)


async def current_principal(request: Request):
    """Dependance FastAPI : retourne le Principal resolu par le middleware.

    Pose par TenantContextMiddleware dans request.state.principal. En
    l'absence de middleware (tests unitaires), on retombe sur l'adapter
    container pour resoudre a la volee - meme contrat que le middleware.
    """
    principal = getattr(request.state, "principal", None)
    if principal is not None:
        return principal
    from ..adapters.container import get_principal
    try:
        return await get_principal(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"auth_failed:{e}") from e


def _is_public(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    for p in ("/docs", "/openapi", "/redoc", "/static", "/billing/webhook"):
        if path.startswith(p):
            return True
    return False


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Resout le Principal via l'adapter, remplit le ContextVar tenant,
    et rejette 401 sur toute route non-publique sans token valide."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        from ..adapters.container import get_principal
        path = request.url.path
        token = _current_tenant.set(None)
        try:
            if _is_public(path):
                return await call_next(request)
            try:
                principal = await get_principal(request)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"auth_failed:{e}") from e
            _current_tenant.set(principal.tenant_id)
            request.state.principal = principal
            return await call_next(request)
        finally:
            _current_tenant.reset(token)
