"""Adapter Microsoft Graph API.

Sprint 1 — implémentation cible :
    * OAuth v2 (Azure AD) : authorize_url, exchange_code, refresh
    * Sync : /me/messages/delta (delta tokens)
    * Send : /me/sendMail

Scopes utilisés :
    - Mail.Read
    - Mail.ReadWrite
    - Mail.Send
    - User.Read
    - offline_access
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Literal
from urllib.parse import urlencode

import httpx
import structlog

from ..config import settings
from .base import MailProvider, RawMessage

log = structlog.get_logger()

SCOPES = [
    "Mail.Read",
    "Mail.ReadWrite",
    "Mail.Send",
    "User.Read",
    "offline_access",
]


def _authority() -> str:
    return f"https://login.microsoftonline.com/{settings.ms_tenant_id}"


AUTH_URL = "{auth}/oauth2/v2.0/authorize"
TOKEN_URL = "{auth}/oauth2/v2.0/token"
API = "https://graph.microsoft.com/v1.0"


class MicrosoftProvider(MailProvider):
    provider_name: Literal["microsoft"] = "microsoft"

    def authorize_url(self, state: str) -> str:
        params = {
            "client_id": settings.ms_client_id,
            "redirect_uri": settings.ms_redirect_uri,
            "response_type": "code",
            "response_mode": "query",
            "scope": " ".join(SCOPES),
            "state": state,
        }
        return AUTH_URL.format(auth=_authority()) + "?" + urlencode(params)

    async def exchange_code(self, code: str) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                TOKEN_URL.format(auth=_authority()),
                data={
                    "client_id": settings.ms_client_id,
                    "client_secret": settings.ms_client_secret.get_secret_value(),
                    "code": code,
                    "redirect_uri": settings.ms_redirect_uri,
                    "grant_type": "authorization_code",
                    "scope": " ".join(SCOPES),
                },
            )
            r.raise_for_status()
            tok = r.json()

            u = await client.get(
                f"{API}/me",
                headers={"Authorization": f"Bearer {tok['access_token']}"},
            )
            u.raise_for_status()
            user = u.json()

        return {
            "access_token": tok["access_token"],
            "refresh_token": tok.get("refresh_token"),
            "expires_at": tok["expires_in"],
            "email": user.get("mail") or user.get("userPrincipalName"),
            "display_name": user.get("displayName"),
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                TOKEN_URL.format(auth=_authority()),
                data={
                    "client_id": settings.ms_client_id,
                    "client_secret": settings.ms_client_secret.get_secret_value(),
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                    "scope": " ".join(SCOPES),
                },
            )
            r.raise_for_status()
            return r.json()

    async def list_initial_messages(
        self, access_token: str, since: datetime
    ) -> AsyncIterator[RawMessage]:
        """/me/messages?$filter=receivedDateTime ge … — paginé via @odata.nextLink."""
        raise NotImplementedError("Microsoft.list_initial_messages — Sprint 1 · BE")

    async def list_incremental(
        self, access_token: str, cursor: str | None
    ) -> tuple[AsyncIterator[RawMessage], str]:
        """/me/mailFolders/inbox/messages/delta — suit deltaToken."""
        raise NotImplementedError("Microsoft.list_incremental — Sprint 1 · BE")

    async def download_attachment(
        self, access_token: str, message_id: str, attachment_id: str
    ) -> bytes:
        raise NotImplementedError("Microsoft.download_attachment — Sprint 1 · BE")

    async def send_message(
        self,
        access_token: str,
        to: list[str],
        cc: list[str],
        subject: str,
        body_text: str,
        body_html: str | None = None,
        in_reply_to_provider_id: str | None = None,
        attachments: list[tuple[str, bytes, str]] | None = None,
    ) -> str:
        """POST /me/sendMail — payload JSON Graph."""
        raise NotImplementedError("Microsoft.send_message — Sprint 3 · BE+FE")
