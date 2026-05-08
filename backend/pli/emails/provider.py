"""Interface EmailProvider + impl multi-backend (memory / smtp / sendgrid / postmark)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
import structlog

from ..config import settings

log = structlog.get_logger()


@dataclass
class SentEmail:
    to: str
    template: str
    subject: str
    context: dict
    provider_msg_id: str | None = None


@dataclass
class EmailMessage:
    to: str
    subject: str
    html: str
    text: str
    template: str
    context: dict = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, msg: EmailMessage) -> str | None:
        """Envoi. Retourne l'ID provider si dispo."""


# ---------------------------------------------------------------------------
# In-memory (dev / tests) — expose la liste des messages envoyés via outbox
# ---------------------------------------------------------------------------


class MemoryEmailProvider(EmailProvider):
    def __init__(self) -> None:
        self.outbox: list[SentEmail] = []

    async def send(self, msg: EmailMessage) -> str | None:
        self.outbox.append(
            SentEmail(to=msg.to, template=msg.template, subject=msg.subject, context=msg.context)
        )
        log.info("memory_email", to=msg.to, template=msg.template)
        return f"mem-{len(self.outbox)}"


# ---------------------------------------------------------------------------
# SMTP (MailHog en dev, Postfix en prod self-hosted)
# ---------------------------------------------------------------------------


class SmtpEmailProvider(EmailProvider):
    async def send(self, msg: EmailMessage) -> str | None:
        import aiosmtplib  # lazy import

        m = MIMEMultipart("alternative")
        m["From"] = settings.email_from
        m["To"] = msg.to
        m["Subject"] = msg.subject
        m.attach(MIMEText(msg.text, "plain", "utf-8"))
        m.attach(MIMEText(msg.html, "html", "utf-8"))
        for k, v in msg.headers.items():
            m[k] = v
        await aiosmtplib.send(
            m,
            hostname=settings.email_smtp_host,
            port=settings.email_smtp_port,
            username=settings.email_smtp_user,
            password=settings.email_smtp_password.get_secret_value()
            if settings.email_smtp_password
            else None,
            start_tls=settings.email_smtp_port not in (25, 1025),
        )
        return None


# ---------------------------------------------------------------------------
# SendGrid (API HTTP)
# ---------------------------------------------------------------------------


class SendGridEmailProvider(EmailProvider):
    URL = "https://api.sendgrid.com/v3/mail/send"

    async def send(self, msg: EmailMessage) -> str | None:
        if not settings.email_api_key:
            raise RuntimeError("PLI_EMAIL_API_KEY manquant pour sendgrid")
        payload = {
            "personalizations": [{"to": [{"email": msg.to}]}],
            "from": {"email": settings.email_from, "name": "PLI"},
            "subject": msg.subject,
            "content": [
                {"type": "text/plain", "value": msg.text},
                {"type": "text/html", "value": msg.html},
            ],
            "headers": msg.headers,
        }
        async with httpx.AsyncClient(timeout=10) as cli:
            r = await cli.post(
                self.URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.email_api_key.get_secret_value()}",
                    "Content-Type": "application/json",
                },
            )
        if r.status_code >= 400:
            log.error("sendgrid_error", status=r.status_code, body=r.text)
            r.raise_for_status()
        return r.headers.get("X-Message-Id")


# ---------------------------------------------------------------------------
# Postmark (API HTTP)
# ---------------------------------------------------------------------------


class PostmarkEmailProvider(EmailProvider):
    URL = "https://api.postmarkapp.com/email"

    async def send(self, msg: EmailMessage) -> str | None:
        if not settings.email_api_key:
            raise RuntimeError("PLI_EMAIL_API_KEY manquant pour postmark")
        payload = {
            "From": settings.email_from,
            "To": msg.to,
            "Subject": msg.subject,
            "HtmlBody": msg.html,
            "TextBody": msg.text,
            "MessageStream": "outbound",
            "Headers": [{"Name": k, "Value": v} for k, v in msg.headers.items()],
        }
        async with httpx.AsyncClient(timeout=10) as cli:
            r = await cli.post(
                self.URL,
                json=payload,
                headers={
                    "X-Postmark-Server-Token": settings.email_api_key.get_secret_value(),
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
        r.raise_for_status()
        return r.json().get("MessageID")


# ---------------------------------------------------------------------------
# Singleton selon configuration
# ---------------------------------------------------------------------------

_provider: EmailProvider | None = None


def get_email_provider() -> EmailProvider:
    global _provider
    if _provider is not None:
        return _provider
    match settings.email_provider:
        case "memory":
            _provider = MemoryEmailProvider()
        case "smtp":
            _provider = SmtpEmailProvider()
        case "sendgrid":
            _provider = SendGridEmailProvider()
        case "postmark":
            _provider = PostmarkEmailProvider()
        case other:
            raise RuntimeError(f"PLI_EMAIL_PROVIDER inconnu: {other}")
    return _provider


def reset_provider_for_tests() -> None:
    global _provider
    _provider = None
