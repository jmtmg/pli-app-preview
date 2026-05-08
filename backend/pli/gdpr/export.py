"""
GDPR — Droit à la portabilité (RGPD art. 20).

Génère un ZIP contenant :
- messages/<account>/<year>/<uuid>.eml   (un fichier EML par message, RFC 5322)
- contacts.vcf                            (vCard 4.0, tous les contacts)
- metadata.json                           (épinglages, filtres, settings, historique abo)
- README.txt                              (explication, licence, mentions)

Le ZIP est chiffré au repos (S3 + SSE), téléchargé via URL présignée (24 h).
"""

from __future__ import annotations

import io
import json
import logging
import uuid
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum

from sqlalchemy.orm import Session

from pli.db import get_session
from pli.models import (
    Account,
    AuditLog,
    Contact,
    ExportJob,
    Message,
    User,
)
from pli.storage import get_storage

log = logging.getLogger(__name__)

EXPORT_URL_TTL = timedelta(hours=24)
EXPORT_RETENTION = timedelta(days=7)
README_TEXT = """\
# Export de vos données PLI

Cet export contient l'intégralité des données que PLI détient sur vous, au
format ouvert et portable, conformément à l'article 20 RGPD.

Contenu :
- messages/<compte>/<année>/<uuid>.eml  : un fichier .eml par email, compatible
  avec Thunderbird, Apple Mail, Outlook (import : "Fichier > Importer").
- contacts.vcf                          : vos contacts au format vCard 4.0.
- metadata.json                         : paramètres, épinglages, historique
  d'abonnement (lisible avec tout éditeur de texte).

Cet export est généré à votre demande. Vous pouvez également supprimer votre
compte à tout moment depuis Paramètres > Mes données.

Pour toute question : dpo@pli.app
"""


class ExportStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class ExportJobView:
    job_id: str
    status: ExportStatus
    created_at: datetime
    expires_at: datetime | None
    download_url: str | None
    size_bytes: int | None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def enqueue_export(user_id: uuid.UUID, session: Session | None = None) -> ExportJobView:
    """Crée un job d'export et délègue au worker. Non bloquant."""
    session = session or get_session()
    job = ExportJob(
        id=uuid.uuid4(),
        user_id=user_id,
        status=ExportStatus.PENDING.value,
        created_at=datetime.now(UTC),
    )
    session.add(job)
    session.add(
        AuditLog(
            user_id=user_id,
            action="gdpr.export.requested",
            resource_id=str(job.id),
            created_at=job.created_at,
        )
    )
    session.commit()

    # Dispatch to Celery/RQ worker.
    from pli.tasks import run_export_job

    run_export_job.delay(str(job.id))

    return _view(job)


def get_export_status(
    user_id: uuid.UUID, job_id: uuid.UUID, session: Session | None = None
) -> ExportJobView | None:
    session = session or get_session()
    job = (
        session.query(ExportJob)
        .filter(ExportJob.id == job_id, ExportJob.user_id == user_id)
        .one_or_none()
    )
    if job is None:
        return None

    # Auto-expire if URL past TTL.
    if (
        job.status == ExportStatus.READY.value
        and job.expires_at
        and job.expires_at < datetime.now(UTC)
    ):
        job.status = ExportStatus.EXPIRED.value
        session.commit()

    return _view(job)


def build_export_archive(job_id: uuid.UUID) -> None:
    """
    Worker entrypoint. Builds the ZIP, uploads encrypted to S3, stores presigned URL.
    Safe to retry (idempotent on job row).
    """
    session = get_session()
    storage = get_storage()

    job = session.query(ExportJob).filter(ExportJob.id == job_id).one()
    if job.status not in (ExportStatus.PENDING.value, ExportStatus.FAILED.value):
        log.info("export job %s already in status %s, skipping", job.id, job.status)
        return

    job.status = ExportStatus.RUNNING.value
    session.commit()

    try:
        user: User = session.query(User).filter(User.id == job.user_id).one()
        archive = _assemble_zip(session, user)
        key = f"exports/{user.id}/{job.id}.zip"
        storage.put(key, archive, content_type="application/zip", encrypt=True)

        job.object_key = key
        job.size_bytes = len(archive)
        job.status = ExportStatus.READY.value
        job.ready_at = datetime.now(UTC)
        job.expires_at = job.ready_at + EXPORT_URL_TTL
        session.add(
            AuditLog(
                user_id=user.id,
                action="gdpr.export.ready",
                resource_id=str(job.id),
                created_at=job.ready_at,
            )
        )
        session.commit()
    except Exception as exc:  # noqa: BLE001 — broad by design
        log.exception("export job %s failed", job.id)
        job.status = ExportStatus.FAILED.value
        job.error_message = str(exc)[:2000]
        session.commit()
        raise


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _assemble_zip(session: Session, user: User) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README_TEXT)
        zf.writestr("metadata.json", _metadata_json(session, user))
        zf.writestr("contacts.vcf", _contacts_vcf(session, user))
        for account in session.query(Account).filter(Account.user_id == user.id).all():
            for eml_path, eml_bytes in _messages_for_account(session, account):
                zf.writestr(eml_path, eml_bytes)
    return buffer.getvalue()


def _metadata_json(session: Session, user: User) -> str:
    accounts = session.query(Account).filter(Account.user_id == user.id).all()
    payload = {
        "export_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "locale": user.locale,
            "plan": user.plan,
        },
        "accounts": [
            {
                "id": str(a.id),
                "provider": a.provider,
                "email": a.email,
                "connected_at": a.created_at.isoformat(),
            }
            for a in accounts
        ],
        "settings": user.settings or {},
        "pinned_contacts": user.pinned_contacts or [],
        "subscription_history": _subscription_history(session, user),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _contacts_vcf(session: Session, user: User) -> str:
    contacts: Iterable[Contact] = (
        session.query(Contact).filter(Contact.user_id == user.id).order_by(Contact.name).all()
    )
    blocks: list[str] = []
    for c in contacts:
        lines = ["BEGIN:VCARD", "VERSION:4.0"]
        if c.name:
            lines.append(f"FN:{_escape_vcf(c.name)}")
        if c.email:
            lines.append(f"EMAIL;TYPE=INTERNET:{c.email}")
        if c.company:
            lines.append(f"ORG:{_escape_vcf(c.company)}")
        if c.role:
            lines.append(f"TITLE:{_escape_vcf(c.role)}")
        if c.phone:
            lines.append(f"TEL:{c.phone}")
        if c.notes:
            lines.append(f"NOTE:{_escape_vcf(c.notes)}")
        lines.append(f"UID:urn:uuid:{c.id}")
        lines.append(f"REV:{c.updated_at.strftime('%Y%m%dT%H%M%SZ')}")
        lines.append("END:VCARD")
        blocks.append("\r\n".join(lines))
    return "\r\n".join(blocks) + ("\r\n" if blocks else "")


def _messages_for_account(session: Session, account: Account):
    """Yield (path_in_zip, eml_bytes) tuples. Streaming-friendly."""
    query = (
        session.query(Message)
        .filter(Message.account_id == account.id)
        .order_by(Message.received_at)
    )
    for msg in query.yield_per(100):
        year = msg.received_at.strftime("%Y") if msg.received_at else "unknown"
        safe_account = account.email.replace("/", "_").replace("@", "_at_")
        path = f"messages/{safe_account}/{year}/{msg.id}.eml"
        yield path, _message_to_eml(msg)


def _message_to_eml(msg: Message) -> bytes:
    """
    Rebuild a RFC 5322 .eml from the stored headers + body. If raw source is
    preserved we return it directly; otherwise we assemble a minimal message.
    """
    if msg.raw_source:
        return msg.raw_source
    # Minimal reconstruction — still openable by mail clients.
    hdrs = msg.headers or {}
    out: list[str] = []
    for key in (
        "From",
        "To",
        "Cc",
        "Bcc",
        "Subject",
        "Date",
        "Message-ID",
        "In-Reply-To",
        "References",
    ):
        if key in hdrs and hdrs[key]:
            out.append(f"{key}: {hdrs[key]}")
    out.append("MIME-Version: 1.0")
    out.append('Content-Type: text/html; charset="utf-8"')
    out.append("")
    out.append(msg.body_html or msg.body_text or "")
    return "\r\n".join(out).encode("utf-8", errors="replace")


def _escape_vcf(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _subscription_history(session: Session, user: User) -> list[dict]:
    # Placeholder — wired to the billing module in sprint 6.
    try:
        from pli.billing import list_user_events

        return [evt.as_dict() for evt in list_user_events(session, user.id)]
    except Exception:  # noqa: BLE001
        return []


def _view(job: ExportJob) -> ExportJobView:
    url: str | None = None
    if job.status == ExportStatus.READY.value and job.object_key:
        storage = get_storage()
        url = storage.presigned_url(job.object_key, expires_in=EXPORT_URL_TTL)
    return ExportJobView(
        job_id=str(job.id),
        status=ExportStatus(job.status),
        created_at=job.created_at,
        expires_at=job.expires_at,
        download_url=url,
        size_bytes=job.size_bytes,
    )


def cleanup_expired_exports() -> None:
    """Called by daily cron. Purges S3 objects and marks rows EXPIRED."""
    session = get_session()
    storage = get_storage()
    cutoff = datetime.now(UTC) - EXPORT_RETENTION
    stale = (
        session.query(ExportJob)
        .filter(ExportJob.ready_at.isnot(None), ExportJob.ready_at < cutoff)
        .all()
    )
    for job in stale:
        if job.object_key:
            try:
                storage.delete(job.object_key)
            except Exception:  # noqa: BLE001
                log.warning("failed to delete export object %s", job.object_key)
        job.status = ExportStatus.EXPIRED.value
        job.object_key = None
    session.commit()
