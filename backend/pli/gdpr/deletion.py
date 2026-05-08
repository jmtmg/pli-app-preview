"""
GDPR — Droit à l'effacement (RGPD art. 17).

Schéma :
- L'utilisateur déclenche `schedule_account_deletion` : son compte passe en
  statut `scheduled_for_deletion`, avec `purge_at = now + 30 jours`.
- Pendant 30 jours, il peut se reconnecter et annuler via
  `cancel_account_deletion`. Les sessions restent révoquées.
- Un cron quotidien `purge_scheduled_accounts` purge les comptes dont
  `purge_at < now` :
  * révocation tokens OAuth côté provider (Gmail / Microsoft)
  * suppression lignes DB : messages, contacts, attachments, accounts,
    sessions, export_jobs, audit_log (anonymisé), user
  * suppression objets stockage (pièces jointes + exports)
  * invalidation caches
- Données conservées malgré la purge (cadre légal) :
  * factures : 10 ans (Code de commerce L123-22)
  * logs de connexion : 12 mois (LCEN art. 6-II), pseudonymisés
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from pli.db import get_session
from pli.models import (
    Account,
    Attachment,
    AuditLog,
    Contact,
    ExportJob,
    Message,
    RefreshToken,
    User,
)
from pli.models import (
    Session as UserSession,
)
from pli.providers import get_provider
from pli.security.passwords import verify_password
from pli.storage import get_storage

log = logging.getLogger(__name__)

DELETION_WINDOW = timedelta(days=30)


class DeletionError(Exception):
    pass


class WrongPasswordError(DeletionError):
    pass


class NotScheduledError(DeletionError):
    pass


@dataclass
class DeletionState:
    scheduled: bool
    purge_at: datetime | None
    scheduled_at: datetime | None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def schedule_account_deletion(
    user_id: uuid.UUID,
    password_confirmation: str,
    session: Session | None = None,
) -> DeletionState:
    """Ordonne la suppression. Révoque les sessions immédiatement (mais l'user peut
    encore se reconnecter pour annuler pendant la fenêtre de 30 j)."""
    session = session or get_session()
    user: User = session.query(User).filter(User.id == user_id).one()

    if not verify_password(password_confirmation, user.password_hash):
        raise WrongPasswordError("mot de passe incorrect")

    now = datetime.now(UTC)
    user.scheduled_for_deletion_at = now
    user.purge_at = now + DELETION_WINDOW

    # Invalidate all refresh tokens now.
    session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now, revoked_reason="account_deletion_requested")
    )
    session.execute(delete(UserSession).where(UserSession.user_id == user_id))

    session.add(
        AuditLog(
            user_id=user_id,
            action="gdpr.deletion.scheduled",
            resource_id=str(user_id),
            created_at=now,
            metadata={"purge_at": user.purge_at.isoformat()},
        )
    )
    session.commit()

    _send_deletion_scheduled_email(user, purge_at=user.purge_at)

    return DeletionState(
        scheduled=True, purge_at=user.purge_at, scheduled_at=user.scheduled_for_deletion_at
    )


def cancel_account_deletion(user_id: uuid.UUID, session: Session | None = None) -> DeletionState:
    """Annulation dans la fenêtre des 30 j."""
    session = session or get_session()
    user: User = session.query(User).filter(User.id == user_id).one()

    if user.scheduled_for_deletion_at is None:
        raise NotScheduledError("aucune suppression programmée")

    now = datetime.now(UTC)
    user.scheduled_for_deletion_at = None
    user.purge_at = None

    session.add(
        AuditLog(
            user_id=user_id,
            action="gdpr.deletion.cancelled",
            resource_id=str(user_id),
            created_at=now,
        )
    )
    session.commit()

    _send_deletion_cancelled_email(user)

    return DeletionState(scheduled=False, purge_at=None, scheduled_at=None)


def get_deletion_state(user_id: uuid.UUID, session: Session | None = None) -> DeletionState:
    session = session or get_session()
    user: User = session.query(User).filter(User.id == user_id).one()
    return DeletionState(
        scheduled=user.scheduled_for_deletion_at is not None,
        purge_at=user.purge_at,
        scheduled_at=user.scheduled_for_deletion_at,
    )


def purge_scheduled_accounts(now: datetime | None = None) -> int:
    """
    Cron daily. Purge all accounts whose `purge_at` is in the past.
    Returns the number of accounts purged.
    """
    session = get_session()
    now = now or datetime.now(UTC)
    accounts_to_purge: list[User] = (
        session.query(User).filter(User.purge_at.isnot(None), User.purge_at <= now).all()
    )

    purged = 0
    for user in accounts_to_purge:
        try:
            _purge_single_user(session, user)
            purged += 1
        except Exception:  # noqa: BLE001
            log.exception("purge failed for user %s", user.id)
            # Don't raise — we want the cron to continue with other users.
            session.rollback()
    return purged


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _purge_single_user(session: Session, user: User) -> None:
    storage = get_storage()
    user_id = user.id
    log.info("purging user %s", user_id)

    # 1. Revoke OAuth tokens provider-side (best effort, non-bloquant).
    for account in session.query(Account).filter(Account.user_id == user_id).all():
        try:
            provider = get_provider(account.provider)
            provider.revoke_tokens(account)
        except Exception:  # noqa: BLE001
            log.warning("provider %s revoke failed for account %s", account.provider, account.id)

    # 2. Remove stored attachments + exports from object storage.
    attachment_keys = [
        a.object_key
        for a in session.query(Attachment)
        .join(Message, Attachment.message_id == Message.id)
        .join(Account, Message.account_id == Account.id)
        .filter(Account.user_id == user_id)
        .all()
        if a.object_key
    ]
    export_keys = [
        j.object_key
        for j in session.query(ExportJob).filter(ExportJob.user_id == user_id).all()
        if j.object_key
    ]
    for key in attachment_keys + export_keys:
        try:
            storage.delete(key)
        except Exception:  # noqa: BLE001
            log.warning("storage delete failed for %s", key)

    # 3. Delete DB rows (order matters due to FK constraints).
    account_ids = [
        row.id for row in session.query(Account.id).filter(Account.user_id == user_id).all()
    ]
    if account_ids:
        msg_ids = [
            row.id
            for row in session.query(Message.id).filter(Message.account_id.in_(account_ids)).all()
        ]
        if msg_ids:
            session.execute(delete(Attachment).where(Attachment.message_id.in_(msg_ids)))
            session.execute(delete(Message).where(Message.id.in_(msg_ids)))
    session.execute(delete(Account).where(Account.user_id == user_id))
    session.execute(delete(Contact).where(Contact.user_id == user_id))
    session.execute(delete(ExportJob).where(ExportJob.user_id == user_id))
    session.execute(delete(UserSession).where(UserSession.user_id == user_id))
    session.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))

    # 4. Anonymize audit log entries (keep for 12 months per LCEN, but remove PII).
    anon_id = f"anon-{uuid.uuid4()}"
    session.execute(
        update(AuditLog).where(AuditLog.user_id == user_id).values(user_id=None, pseudonym=anon_id)
    )

    # 5. Delete the user row.
    session.execute(delete(User).where(User.id == user_id))

    # 6. Audit trail — final.
    session.add(
        AuditLog(
            user_id=None,
            pseudonym=anon_id,
            action="gdpr.deletion.purged",
            resource_id=str(user_id),
            created_at=datetime.now(UTC),
        )
    )
    session.commit()
    _send_deletion_completed_email(user)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


def _send_deletion_scheduled_email(user: User, purge_at: datetime) -> None:
    from pli.mail import send_transactional

    send_transactional(
        to=user.email,
        template="gdpr_deletion_scheduled",
        locale=user.locale or "fr",
        vars={
            "name": user.display_name or user.email,
            "purge_date": purge_at.strftime("%d/%m/%Y"),
            "cancel_url": "https://pli.app/settings/my-data",
        },
    )


def _send_deletion_cancelled_email(user: User) -> None:
    from pli.mail import send_transactional

    send_transactional(
        to=user.email,
        template="gdpr_deletion_cancelled",
        locale=user.locale or "fr",
        vars={"name": user.display_name or user.email},
    )


def _send_deletion_completed_email(user: User) -> None:
    from pli.mail import send_transactional

    send_transactional(
        to=user.email,
        template="gdpr_deletion_completed",
        locale=user.locale or "fr",
        vars={"name": user.display_name or user.email},
    )
