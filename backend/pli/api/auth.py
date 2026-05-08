"""Router OAuth — connexion d'un compte Gmail ou Microsoft.

Flow :
    GET  /auth/{provider}/start     → redirect vers consent provider
    GET  /auth/{provider}/callback  → échange code, upsert account, kick-off sync initiale

Provider-name source de vérité = schéma SQL (`gmail` | `microsoft`).
"""

from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx
import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import RedirectResponse

from ..accounts_repo import upsert_from_oauth
from ..config import settings
from ..providers import get_provider
from ..sync import sync_account

router = APIRouter()
log = structlog.get_logger()

_SUPPORTED = {"gmail", "microsoft"}

# Stockage in-memory des `state` CSRF.
# Acceptable en Sprint 1 (mode local, 1 process). Sera migré vers signed-cookie
# en M3 (cf. ADR-008).
_STATE_STORE: dict[str, str] = {}


def _redirect_error(reason: str, provider: str | None = None) -> RedirectResponse:
    """Redirige le navigateur vers la page d'erreur frontale avec motif exploitable."""
    params = {"reason": reason}
    if provider:
        params["provider"] = provider
    url = f"{settings.app_url.rstrip('/')}/auth/error?{urlencode(params)}"
    return RedirectResponse(url, status_code=307)


@router.get("/{provider}/start", summary="Démarrer OAuth")
def start(provider: str) -> RedirectResponse:
    if provider not in _SUPPORTED:
        raise HTTPException(400, f"Provider inconnu — attendu : {sorted(_SUPPORTED)}")
    state = secrets.token_urlsafe(24)
    _STATE_STORE[state] = provider
    url = get_provider(provider).authorize_url(state)
    log.info("oauth_start", provider=provider, state_issued=True)
    return RedirectResponse(url, status_code=307)


@router.get("/{provider}/callback", summary="Callback OAuth")
async def callback(
    provider: str,
    bg: BackgroundTasks,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> RedirectResponse:
    """Finalise l'échange OAuth, crée/réactive l'account et lance la sync initiale.

    Cas d'erreur → redirect vers la page frontale `/auth/error?reason=...` avec
    un motif stable et traduisible côté UI. Ne jamais exposer de stacktrace à
    l'utilisateur.
    """
    if provider not in _SUPPORTED:
        return _redirect_error("unsupported_provider", provider)

    # Google peut renvoyer `error=access_denied` si l'utilisateur annule
    if error:
        log.warning("oauth_provider_error", provider=provider, error=error)
        return _redirect_error(error, provider)

    if not code or not state:
        log.warning(
            "oauth_missing_params", provider=provider, has_code=bool(code), has_state=bool(state)
        )
        return _redirect_error("missing_code_or_state", provider)

    expected = _STATE_STORE.pop(state, None)
    if expected != provider:
        # State inconnu, expiré ou pour un autre provider → CSRF / replay potentiel
        log.warning("oauth_state_invalid", provider=provider)
        return _redirect_error("invalid_state", provider)

    try:
        tokens = await get_provider(provider).exchange_code(code)
    except httpx.HTTPStatusError as e:
        log.error(
            "oauth_exchange_failed",
            provider=provider,
            status=e.response.status_code,
            body=e.response.text[:500],
        )
        return _redirect_error("token_exchange_failed", provider)
    except httpx.HTTPError as e:
        log.error("oauth_exchange_network", provider=provider, error=str(e))
        return _redirect_error("provider_unreachable", provider)

    email = tokens.get("email")
    access_token = tokens.get("access_token")
    if not isinstance(email, str) or not isinstance(access_token, str):
        log.error("oauth_invalid_token_payload", provider=provider, keys=list(tokens.keys()))
        return _redirect_error("invalid_token_payload", provider)

    refresh_token = tokens.get("refresh_token")
    display_name = tokens.get("display_name")
    expires_in = int(tokens.get("expires_in") or 3600)

    account = upsert_from_oauth(
        provider=provider,  # type: ignore[arg-type]  # contraint par _SUPPORTED
        email=email,
        display_name=display_name if isinstance(display_name, str) else None,
        access_token=access_token,
        refresh_token=refresh_token if isinstance(refresh_token, str) else None,
        expires_in_seconds=expires_in,
    )

    # Kick-off sync initiale en arrière-plan — n'alourdit pas le callback
    bg.add_task(sync_account, account.id, "initial")

    # Retour UX : frontend = liste conversations filtrée sur ce compte fraîchement connecté
    redirect = f"{settings.app_url.rstrip('/')}/?connected={account.id}"
    return RedirectResponse(redirect, status_code=307)
