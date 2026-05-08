"""Interface `MailProvider` commune à Gmail et Microsoft Graph.

Principe clé : le reste du backend ne connaît que cette interface. Chaque adapter
transforme le format natif en `RawMessage` (DTO brut, sans logique de persistance).
La normalisation → `Message` se fait dans `sync/parser.py`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class RawMessage:
    """Représentation brute d'un message, pré-normalisation."""

    provider_id: str
    thread_id: str | None
    subject: str | None
    from_email: str
    from_name: str | None
    to_emails: list[str]
    cc_emails: list[str]
    received_at: datetime
    body_text: str | None
    body_html: str | None
    snippet: str | None
    is_read: bool
    headers: dict[str, str]
    attachment_refs: list[RawAttachmentRef] = field(default_factory=list)


@dataclass
class RawAttachmentRef:
    provider_id: str
    filename: str
    mime_type: str
    size_bytes: int


class MailProvider(ABC):
    """Contrat commun à tout provider de mail."""

    provider_name: Literal["gmail", "microsoft"]

    # ---- OAuth ----
    @abstractmethod
    def authorize_url(self, state: str) -> str: ...

    @abstractmethod
    async def exchange_code(self, code: str) -> dict[str, object]:
        """Retourne {access_token, refresh_token, expires_at, email, display_name}."""

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> dict[str, object]: ...

    # ---- Sync ----
    @abstractmethod
    async def list_initial_messages(
        self, access_token: str, since: datetime
    ) -> AsyncIterator[RawMessage]:
        """Itère les messages depuis `since` (sync initiale)."""
        # Note: type-ignore for ABC pattern with async generators
        if False:
            yield  # pragma: no cover

    @abstractmethod
    async def list_incremental(
        self, access_token: str, cursor: str | None
    ) -> tuple[AsyncIterator[RawMessage], str]:
        """Retourne (iterator de messages delta, nouveau cursor)."""

    @abstractmethod
    async def download_attachment(
        self, access_token: str, message_id: str, attachment_id: str
    ) -> bytes: ...

    # ---- Send ----
    @abstractmethod
    async def send_message(
        self,
        access_token: str,
        to: list[str],
        cc: list[str],
        subject: str,
        body_text: str,
        body_html: str | None = None,
        in_reply_to_provider_id: str | None = None,
        attachments: list[tuple[str, bytes, str]] | None = None,  # (filename, bytes, mime)
    ) -> str:
        """Retourne le provider_id du message envoyé."""


def get_provider(provider: str) -> MailProvider:
    """Factory — sélectionne l'adapter selon le provider de l'account."""
    from .gmail import GmailProvider
    from .microsoft import MicrosoftProvider

    match provider:
        case "gmail":
            return GmailProvider()
        case "microsoft":
            return MicrosoftProvider()
        case _:
            raise ValueError(f"Provider inconnu : {provider}")
