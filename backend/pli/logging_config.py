"""Configuration structlog + middleware HTTP.

US-1.9 Sprint 1 · owner SRE.

Principes :
- Un seul endroit pour brancher les processors structlog (dev vs prod).
- En mode `local` : sortie console colorisee, lisible par un humain.
- En mode `cloud` : sortie JSON, ingerable par un agregateur (Loki/Datadog).
- Chaque requete HTTP logge : method, path, status, duration_ms, request_id
  (genere si absent de l'en-tete `X-Request-Id`).
- Les donnees PII (emails, tokens) ne sont JAMAIS loggees au niveau HTTP ;
  les handlers metier peuvent en logger mais doivent hasher si besoin.
"""

from __future__ import annotations

import logging
import secrets
import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


def configure_logging() -> None:
    """Branche les processors structlog et la verbosite stdlib."""
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.mode == "local":
        # Dev : rendu console pretty + noms de fichiers
        shared_processors.append(
            structlog.processors.CallsiteParameterAdder(
                parameters={
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            )
        )
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # Cloud : JSON une ligne par log
        shared_processors.append(structlog.processors.format_exc_info)
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logue chaque requete avec duration_ms, status, request_id.

    Le `request_id` est soit lu depuis `X-Request-Id` (fourni par un reverse
    proxy en amont), soit genere ici. Il est propage dans le log via les
    structlog contextvars pour tous les loggers appeles pendant la requete.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        req_id = request.headers.get("x-request-id") or secrets.token_hex(8)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=req_id,
            method=request.method,
            path=request.url.path,
        )
        log = structlog.get_logger()
        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            # On logge en `info` pour 2xx/3xx, `warning` pour 4xx, `error` pour 5xx.
            if status >= 500:
                log.error("http_request", status=status, duration_ms=duration_ms)
            elif status >= 400:
                log.warning("http_request", status=status, duration_ms=duration_ms)
            else:
                log.info("http_request", status=status, duration_ms=duration_ms)
            structlog.contextvars.clear_contextvars()
