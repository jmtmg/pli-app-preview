"""Adapter Gmail API.

Sprint 1 — implémentation cible :
    * OAuth : authorize_url, exchange_code, refresh_access_token
    * Sync : list_initial_messages (Q: "newer_than:30d"), list_incremental (historyId)
    * Send : send_message via users.messages.send

Scopes OAuth utilisés :
    - https://www.googleapis.com/auth/gmail.readonly
    - https://www.googleapis.com/auth/gmail.send
    - https://www.googleapis.com/auth/gmail.modify
    - https://www.googleapis.com/auth/userinfo.email
"""

from __future__ import annotations

import base64
import email.utils
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import urlencode

import httpx
import structlog

from ..config import settings
from .base import MailProvider, RawAttachmentRef, RawMessage

log = structlog.get_logger()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://gmail.googleapis.com/gmail/v1"

# Gmail users.messages.list max page size = 500, mais au-dela de 100 le payload
# devient lourd et la pagination ralentit. 100 = sweet spot documente.
_PAGE_SIZE = 100


class GmailProvider(MailProvider):
    provider_name: Literal["gmail"] = "gmail"

    # ---- OAuth ----
    def authorize_url(self, state: str) -> str:
        params = {
            "client_id": settings.gmail_client_id,
            "redirect_uri": settings.gmail_redirect_uri,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.gmail_client_id,
                    "client_secret": settings.gmail_client_secret.get_secret_value(),
                    "redirect_uri": settings.gmail_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            r.raise_for_status()
            tok = r.json()
            u = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tok['access_token']}"},
            )
            u.raise_for_status()
            user = u.json()
        return {
            "access_token": tok["access_token"],
            "refresh_token": tok.get("refresh_token"),
            "expires_in": int(tok.get("expires_in", 3600)),
            "email": user["email"],
            "display_name": user.get("name"),
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": settings.gmail_client_id,
                    "client_secret": settings.gmail_client_secret.get_secret_value(),
                    "grant_type": "refresh_token",
                },
            )
            r.raise_for_status()
            return r.json()

    # ---- Sync ----
    async def list_initial_messages(
        self, access_token: str, since: datetime
    ) -> AsyncIterator[RawMessage]:
        """Iteres les messages depuis `since` via Gmail users.messages.list."""
        q = f"after:{int(since.timestamp())}"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            page_token: str | None = None
            while True:
                params: dict[str, str | int] = {
                    "q": q,
                    "maxResults": _PAGE_SIZE,
                    "fields": "messages(id,threadId),nextPageToken",
                }
                if page_token:
                    params["pageToken"] = page_token
                r = await client.get(f"{API}/users/me/messages", params=params)
                r.raise_for_status()
                body = r.json()
                messages = body.get("messages") or []
                log.info(
                    "gmail_list_page",
                    count=len(messages),
                    has_next=bool(body.get("nextPageToken")),
                )
                for meta in messages:
                    detail = await self._fetch_message(client, meta["id"])
                    yield _gmail_to_raw(detail)
                page_token = body.get("nextPageToken")
                if not page_token:
                    return

    async def _fetch_message(self, client: httpx.AsyncClient, message_id: str) -> dict[str, Any]:
        r = await client.get(
            f"{API}/users/me/messages/{message_id}",
            params={"format": "full"},
        )
        r.raise_for_status()
        return r.json()

    async def list_incremental(
        self, access_token: str, cursor: str | None
    ) -> tuple[AsyncIterator[RawMessage], str]:
        raise NotImplementedError("Gmail.list_incremental - Sprint 2")

    async def download_attachment(
        self, access_token: str, message_id: str, attachment_id: str
    ) -> bytes:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=60, headers=headers) as client:
            r = await client.get(
                f"{API}/users/me/messages/{message_id}/attachments/{attachment_id}"
            )
            r.raise_for_status()
            data = r.json().get("data", "")
            return _b64url_decode(data)

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
        raise NotImplementedError("Gmail.send_message - Sprint 3")


# -- Parsing helpers --


def _b64url_decode(data: str) -> bytes:
    if not data:
        return b""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _header(headers: list[dict[str, str]], name: str) -> str | None:
    target = name.lower()
    for h in headers:
        if h.get("name", "").lower() == target:
            return h.get("value")
    return None


def _split_addresses(raw: str | None) -> list[str]:
    if not raw:
        return []
    pairs = email.utils.getaddresses([raw])
    return [addr for _, addr in pairs if addr]


def _parse_from(raw: str | None) -> tuple[str, str | None]:
    if not raw:
        return "", None
    name, addr = email.utils.parseaddr(raw)
    return addr, (name or None)


def _walk_parts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    def _walk(node: dict[str, Any]) -> None:
        parts = node.get("parts")
        if parts:
            for p in parts:
                _walk(p)
        else:
            out.append(node)

    _walk(payload)
    return out


def _extract_bodies(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    text: str | None = None
    html: str | None = None
    for part in _walk_parts(payload):
        mime = part.get("mimeType", "")
        data = (part.get("body") or {}).get("data")
        if not data:
            continue
        try:
            decoded = _b64url_decode(data).decode("utf-8", errors="replace")
        except Exception:
            continue
        if mime == "text/plain" and text is None:
            text = decoded
        elif mime == "text/html" and html is None:
            html = decoded
    return text, html


def _extract_attachment_refs(payload: dict[str, Any]) -> list[RawAttachmentRef]:
    refs: list[RawAttachmentRef] = []
    for part in _walk_parts(payload):
        body = part.get("body") or {}
        att_id = body.get("attachmentId")
        filename = part.get("filename")
        if att_id and filename:
            refs.append(
                RawAttachmentRef(
                    provider_id=att_id,
                    filename=filename,
                    mime_type=part.get("mimeType") or "application/octet-stream",
                    size_bytes=int(body.get("size", 0)),
                )
            )
    return refs


def _gmail_to_raw(msg: dict[str, Any]) -> RawMessage:
    payload = msg.get("payload") or {}
    headers = payload.get("headers") or []
    label_ids = msg.get("labelIds") or []

    from_addr, from_name = _parse_from(_header(headers, "From"))
    received_ms = int(msg.get("internalDate", 0))
    received_at = datetime.fromtimestamp(received_ms / 1000, tz=UTC)

    body_text, body_html = _extract_bodies(payload)
    is_read = "UNREAD" not in label_ids

    return RawMessage(
        provider_id=msg["id"],
        thread_id=msg.get("threadId"),
        subject=_header(headers, "Subject"),
        from_email=from_addr,
        from_name=from_name,
        to_emails=_split_addresses(_header(headers, "To")),
        cc_emails=_split_addresses(_header(headers, "Cc")),
        received_at=received_at,
        body_text=body_text,
        body_html=body_html,
        snippet=msg.get("snippet"),
        is_read=is_read,
        headers={h["name"]: h.get("value", "") for h in headers if "name" in h},
        attachment_refs=_extract_attachment_refs(payload),
    )
