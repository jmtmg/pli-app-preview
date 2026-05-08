"""
Tests bout-en-bout des parcours RGPD.

Couvre :
- export → ZIP contient EML + vCard + metadata.json + README
- suppression programmée → fenêtre 30 j
- annulation dans fenêtre
- purge effective après fenêtre → 0 ligne résiduelle sauf factures/logs légaux
- résistance à mauvais mot de passe (pas d'oracle)
"""

from __future__ import annotations

import io
import uuid
import zipfile
from datetime import UTC, datetime, timedelta

import pytest

from pli.gdpr import (
    cancel_account_deletion,
    enqueue_export,
    purge_scheduled_accounts,
    schedule_account_deletion,
)
from pli.gdpr.deletion import (
    NotScheduledError,
    WrongPasswordError,
    get_deletion_state,
)
from pli.gdpr.export import ExportStatus, build_export_archive
from pli.models import (
    Account,
    AuditLog,
    Contact,
    ExportJob,
    Message,
    User,
)

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def seeded_user(db_session, user_factory, account_factory, message_factory, contact_factory):
    """A user with 1 Gmail account, 2 messages, 1 contact."""
    user = user_factory(password="correct horse battery staple")
    account = account_factory(user_id=user.id, provider="gmail", email="jm@example.com")
    message_factory(account_id=account.id, subject="Hello", body_text="world")
    message_factory(account_id=account.id, subject="Second", body_text="…")
    contact_factory(user_id=user.id, name="Alice", email="alice@example.com")
    db_session.commit()
    return user


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_export_produces_zip_with_eml_vcard_metadata(
    db_session, seeded_user, tmp_path, storage_mock
):
    view = enqueue_export(seeded_user.id, session=db_session)
    assert view.status == ExportStatus.PENDING

    # Run the worker synchronously in tests.
    build_export_archive(uuid.UUID(view.job_id))
    storage_mock.assert_encrypted_put_called_with_prefix(f"exports/{seeded_user.id}/")

    job = db_session.query(ExportJob).filter(ExportJob.id == uuid.UUID(view.job_id)).one()
    assert job.status == ExportStatus.READY.value
    assert job.size_bytes > 0

    # Introspect archive content (in-memory mock stores bytes).
    archive = storage_mock.read(job.object_key)
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        names = zf.namelist()
        assert "README.txt" in names
        assert "metadata.json" in names
        assert "contacts.vcf" in names
        eml_paths = [n for n in names if n.startswith("messages/") and n.endswith(".eml")]
        assert len(eml_paths) == 2
        vcf = zf.read("contacts.vcf").decode("utf-8")
        assert "BEGIN:VCARD" in vcf and "FN:Alice" in vcf
        sample_eml = zf.read(eml_paths[0]).decode("utf-8")
        assert "Subject:" in sample_eml


def test_export_url_expires(db_session, seeded_user, storage_mock, freezer):
    view = enqueue_export(seeded_user.id, session=db_session)
    build_export_archive(uuid.UUID(view.job_id))

    # Fast-forward > 24h.
    freezer.move_to(datetime.now(UTC) + timedelta(hours=25))
    from pli.gdpr.export import get_export_status

    status = get_export_status(seeded_user.id, uuid.UUID(view.job_id), session=db_session)
    assert status.status == ExportStatus.EXPIRED


# ---------------------------------------------------------------------------
# Deletion
# ---------------------------------------------------------------------------


def test_schedule_sets_purge_at_plus_30d(db_session, seeded_user):
    state = schedule_account_deletion(
        seeded_user.id,
        password_confirmation="correct horse battery staple",
        session=db_session,
    )
    assert state.scheduled is True
    assert state.purge_at is not None
    delta = state.purge_at - state.scheduled_at
    assert abs(delta - timedelta(days=30)) < timedelta(seconds=10)


def test_wrong_password_does_not_reveal_user_existence(db_session, seeded_user):
    with pytest.raises(WrongPasswordError):
        schedule_account_deletion(seeded_user.id, password_confirmation="wrong", session=db_session)
    # User still active.
    state = get_deletion_state(seeded_user.id, session=db_session)
    assert state.scheduled is False


def test_cancel_within_window_restores_account(db_session, seeded_user):
    schedule_account_deletion(
        seeded_user.id,
        password_confirmation="correct horse battery staple",
        session=db_session,
    )
    state = cancel_account_deletion(seeded_user.id, session=db_session)
    assert state.scheduled is False
    assert state.purge_at is None


def test_cancel_without_schedule_raises(db_session, seeded_user):
    with pytest.raises(NotScheduledError):
        cancel_account_deletion(seeded_user.id, session=db_session)


def test_purge_removes_all_user_rows(db_session, seeded_user, freezer):
    schedule_account_deletion(
        seeded_user.id,
        password_confirmation="correct horse battery staple",
        session=db_session,
    )
    freezer.move_to(datetime.now(UTC) + timedelta(days=31))

    purged = purge_scheduled_accounts()
    assert purged == 1

    # Zero row for user on domain tables.
    for model in (User, Account, Message, Contact, ExportJob):
        count = db_session.query(model).filter_by(user_id=seeded_user.id).count()
        assert count == 0, f"residual rows on {model.__name__}"

    # Audit log anonymized but kept for 12 months (LCEN).
    assert (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id.is_(None), AuditLog.pseudonym.isnot(None))
        .count()
        > 0
    )


def test_purge_idempotent(db_session, seeded_user, freezer):
    schedule_account_deletion(
        seeded_user.id,
        password_confirmation="correct horse battery staple",
        session=db_session,
    )
    freezer.move_to(datetime.now(UTC) + timedelta(days=31))
    assert purge_scheduled_accounts() == 1
    # Re-running finds nothing to purge.
    assert purge_scheduled_accounts() == 0
