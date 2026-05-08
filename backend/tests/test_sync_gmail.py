"""Tests US-1.4 — sync initiale Gmail.

Couvre :
- parsing Gmail `format=full` vers RawMessage (headers, bodies, attachments)
- upsert contact (dédup par email_normalized)
- idempotence : re-run sans doublon (UNIQUE(account_id, provider_id))
- dénormalisation contact (last_msg_at, unread_count, has_attachments)
- échec provider → sync_log contient l'erreur, pas de messages partiellement commités
"""

from __future__ import annotations

import base64
from datetime import UTC, datetime

import pytest

# ---------------------------------------------------------------------------
# Helpers — factory pour un payload Gmail simulé
# ---------------------------------------------------------------------------


def _b64url(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii").rstrip("=")


def _gmail_msg(
    *,
    msg_id: str = "m1",
    thread_id: str = "t1",
    from_addr: str = "Alice <alice@example.com>",
    to_addr: str = "me@example.com",
    subject: str = "Hello",
    body_text: str = "Bonjour !",
    body_html: str | None = None,
    is_unread: bool = True,
    internal_date_ms: int = 1_713_000_000_000,  # 2024-04-13 ~
    attachments: list[tuple[str, str, int]] | None = None,
    snippet: str = "Bonjour !",
) -> dict:
    """Construit un payload Gmail users.messages.get format=full plausible."""
    headers = [
        {"name": "From", "value": from_addr},
        {"name": "To", "value": to_addr},
        {"name": "Subject", "value": subject},
        {"name": "Date", "value": "Sat, 13 Apr 2024 10:00:00 +0000"},
    ]
    # Parts multipart/alternative + PJ éventuelles
    parts = [
        {"mimeType": "text/plain", "body": {"data": _b64url(body_text), "size": len(body_text)}}
    ]
    if body_html is not None:
        parts.append(
            {"mimeType": "text/html", "body": {"data": _b64url(body_html), "size": len(body_html)}}
        )
    for i, (filename, mime, size) in enumerate(attachments or []):
        parts.append(
            {
                "mimeType": mime,
                "filename": filename,
                "body": {"attachmentId": f"att-{msg_id}-{i}", "size": size},
            }
        )
    labels = ["INBOX"] + (["UNREAD"] if is_unread else [])
    return {
        "id": msg_id,
        "threadId": thread_id,
        "labelIds": labels,
        "snippet": snippet,
        "internalDate": str(internal_date_ms),
        "payload": {
            "mimeType": "multipart/alternative" if body_html else "text/plain",
            "headers": headers,
            "body": {},
            "parts": parts,
        },
    }


# ---------------------------------------------------------------------------
# Parsing _gmail_to_raw
# ---------------------------------------------------------------------------


def test_gmail_to_raw_extracts_headers_and_text_body():
    from pli.providers.gmail import _gmail_to_raw

    raw = _gmail_to_raw(
        _gmail_msg(
            from_addr="Alice Wonder <alice@example.com>",
            to_addr="me@example.com, bob@x.io",
            subject="Sujet réunion",
            body_text="Corps\ndu message",
            is_unread=True,
        )
    )
    assert raw.provider_id == "m1"
    assert raw.thread_id == "t1"
    assert raw.from_email == "alice@example.com"
    assert raw.from_name == "Alice Wonder"
    assert raw.to_emails == ["me@example.com", "bob@x.io"]
    assert raw.subject == "Sujet réunion"
    assert raw.body_text == "Corps\ndu message"
    assert raw.is_read is False  # UNREAD label présent


def test_gmail_to_raw_extracts_html_and_attachments():
    from pli.providers.gmail import _gmail_to_raw

    raw = _gmail_to_raw(
        _gmail_msg(
            body_text="plain",
            body_html="<p>rich</p>",
            attachments=[("contract.pdf", "application/pdf", 12345)],
        )
    )
    assert raw.body_text == "plain"
    assert raw.body_html == "<p>rich</p>"
    assert len(raw.attachment_refs) == 1
    att = raw.attachment_refs[0]
    assert att.filename == "contract.pdf"
    assert att.mime_type == "application/pdf"
    assert att.size_bytes == 12345


def test_gmail_to_raw_read_status_reflects_unread_label():
    from pli.providers.gmail import _gmail_to_raw

    unread = _gmail_to_raw(_gmail_msg(is_unread=True))
    read = _gmail_to_raw(_gmail_msg(is_unread=False))
    assert unread.is_read is False
    assert read.is_read is True


def test_gmail_to_raw_handles_internal_date_ms():
    from pli.providers.gmail import _gmail_to_raw

    raw = _gmail_to_raw(_gmail_msg(internal_date_ms=1_700_000_000_000))
    assert raw.received_at == datetime.fromtimestamp(1_700_000_000, tz=UTC)


# ---------------------------------------------------------------------------
# Sync end-to-end — avec provider stubbé
# ---------------------------------------------------------------------------


@pytest.fixture
def owner_account(isolated_settings):  # type: ignore[no-untyped-def]
    """Crée un compte Gmail en DB comme si OAuth avait réussi."""
    from pli.accounts_repo import upsert_from_oauth

    return upsert_from_oauth(
        provider="gmail",
        email="me@example.com",
        display_name="Me",
        access_token="access-tok",
        refresh_token="refresh-tok",
        expires_in_seconds=3600,
    )


@pytest.fixture
def stub_provider_messages(monkeypatch):  # type: ignore[no-untyped-def]
    """Remplace GmailProvider.list_initial_messages par un async-gen injectable."""
    from pli.providers.gmail import GmailProvider, _gmail_to_raw

    payloads: list[dict] = []

    async def _fake_list(self, access_token, since):  # type: ignore[no-untyped-def]
        for p in payloads:
            yield _gmail_to_raw(p)

    monkeypatch.setattr(GmailProvider, "list_initial_messages", _fake_list)
    return payloads


async def _run_sync(account_id: str, kind: str = "initial") -> dict:
    from pli.sync import sync_account

    return await sync_account(account_id, kind)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_sync_imports_messages_and_creates_contacts(owner_account, stub_provider_messages):
    stub_provider_messages.extend(
        [
            _gmail_msg(
                msg_id="g1",
                from_addr="Alice <alice@example.com>",
                to_addr="me@example.com",
                body_text="hey",
                is_unread=True,
            ),
            _gmail_msg(
                msg_id="g2",
                from_addr="Bob <bob@corp.io>",
                to_addr="me@example.com",
                body_text="ping",
                is_unread=False,
                internal_date_ms=1_713_100_000_000,
            ),
        ]
    )

    res = await _run_sync(owner_account.id, "initial")
    assert res["messages_imported"] == 2

    from pli.db import get_conn

    with get_conn() as conn:
        contacts = conn.execute(
            "SELECT email_normalized, unread_count FROM contacts ORDER BY email_normalized"
        ).fetchall()
        messages = conn.execute(
            "SELECT provider_id, direction, is_read FROM messages ORDER BY provider_id"
        ).fetchall()

    emails = [c["email_normalized"] for c in contacts]
    assert emails == ["alice@example.com", "bob@corp.io"]

    # Alice non lu → unread_count = 1 ; Bob lu → 0
    by_email = {c["email_normalized"]: c["unread_count"] for c in contacts}
    assert by_email["alice@example.com"] == 1
    assert by_email["bob@corp.io"] == 0

    # Tous les messages sont `in` (from ≠ account email)
    assert all(m["direction"] == "in" for m in messages)


@pytest.mark.asyncio
async def test_sync_is_idempotent_on_rerun(owner_account, stub_provider_messages):
    """Un message déjà en DB ne doit pas être recréé (UNIQUE provider_id)."""
    stub_provider_messages.append(_gmail_msg(msg_id="g1", from_addr="Alice <alice@example.com>"))
    await _run_sync(owner_account.id)
    await _run_sync(owner_account.id)

    from pli.db import get_conn

    with get_conn() as conn:
        (n,) = conn.execute("SELECT count(*) FROM messages").fetchone()
        (nc,) = conn.execute("SELECT count(*) FROM contacts").fetchone()
    assert n == 1
    assert nc == 1


@pytest.mark.asyncio
async def test_sync_outgoing_detected_when_from_matches_account(
    owner_account, stub_provider_messages
):
    """Si From == email du compte, direction='out' et contact=destinataire."""
    stub_provider_messages.append(
        _gmail_msg(
            msg_id="g1",
            from_addr="Me <me@example.com>",
            to_addr="alice@example.com",
        )
    )
    await _run_sync(owner_account.id)

    from pli.db import get_conn

    with get_conn() as conn:
        row = conn.execute(
            "SELECT m.direction, c.email_normalized FROM messages m "
            "JOIN contacts c ON m.contact_id = c.id"
        ).fetchone()
    assert row["direction"] == "out"
    assert row["email_normalized"] == "alice@example.com"


@pytest.mark.asyncio
async def test_sync_aggregates_update_contact_denormalized_counters(
    owner_account, stub_provider_messages
):
    # 3 messages d'Alice : 2 non-lus, 1 avec PJ
    stub_provider_messages.extend(
        [
            _gmail_msg(
                msg_id="a1",
                from_addr="Alice <alice@example.com>",
                is_unread=True,
                internal_date_ms=1_713_000_000_000,
            ),
            _gmail_msg(
                msg_id="a2",
                from_addr="Alice <alice@example.com>",
                is_unread=True,
                internal_date_ms=1_713_100_000_000,
                attachments=[("doc.pdf", "application/pdf", 999)],
            ),
            _gmail_msg(
                msg_id="a3",
                from_addr="Alice <alice@example.com>",
                is_unread=False,
                internal_date_ms=1_713_200_000_000,
            ),
        ]
    )
    await _run_sync(owner_account.id)

    from pli.db import get_conn

    with get_conn() as conn:
        row = conn.execute(
            "SELECT last_msg_at, unread_count, has_attachments FROM contacts"
        ).fetchone()
    assert row["last_msg_at"] == 1_713_200_000  # le plus récent (en secondes)
    assert row["unread_count"] == 2
    assert row["has_attachments"] == 1


@pytest.mark.asyncio
async def test_sync_failure_is_logged_and_raises(owner_account, monkeypatch):
    """Si le provider lève en cours d'itération, sync_log doit porter l'erreur.

    On bypasse tenacity en appelant la coroutine sous-jacente via `__wrapped__`
    pour éviter les 4 retries avec backoff exponentiel (~14s sinon).
    """
    from pli.providers.gmail import GmailProvider

    async def _fail(self, access_token, since):  # type: ignore[no-untyped-def]
        raise RuntimeError("boom")
        yield  # pragma: no cover — never reached, juste pour en faire un async-gen

    monkeypatch.setattr(GmailProvider, "list_initial_messages", _fail)

    from pli.sync.service import sync_account

    # tenacity conserve la coroutine originale sous __wrapped__ — on bypasse le retry
    unwrapped = sync_account.__wrapped__

    with pytest.raises(RuntimeError):
        await unwrapped(owner_account.id, "initial")

    from pli.db import get_conn

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT kind, error, messages_imported FROM sync_log WHERE account_id = ? ORDER BY id",
            (owner_account.id,),
        ).fetchall()
    assert len(rows) == 1
    assert rows[0]["error"] == "boom"
    assert rows[0]["messages_imported"] == 0


@pytest.mark.asyncio
async def test_sync_skips_messages_with_invalid_email(owner_account, stub_provider_messages):
    """Un message avec from_email vide ne doit pas crasher la sync."""
    stub_provider_messages.extend(
        [
            _gmail_msg(msg_id="ok", from_addr="Alice <alice@example.com>"),
            _gmail_msg(msg_id="bad", from_addr=""),  # email manquant
        ]
    )
    res = await _run_sync(owner_account.id)
    # 1 importé, 1 skippé — pas de crash
    assert res["messages_imported"] == 1
    from pli.db import get_conn

    with get_conn() as conn:
        (n,) = conn.execute("SELECT count(*) FROM messages").fetchone()
    assert n == 1


@pytest.mark.asyncio
async def test_sync_normalizes_alias_and_case_to_dedupe_contacts(
    owner_account, stub_provider_messages
):
    """Alice+promo@gmail.com et Alice@GMAIL.COM → un seul contact."""
    stub_provider_messages.extend(
        [
            _gmail_msg(msg_id="x1", from_addr="Alice <Alice+promo@Gmail.com>"),
            _gmail_msg(
                msg_id="x2", from_addr="Alice <alice@gmail.com>", internal_date_ms=1_713_500_000_000
            ),
        ]
    )
    await _run_sync(owner_account.id)
    from pli.db import get_conn

    with get_conn() as conn:
        contacts = conn.execute("SELECT email_normalized FROM contacts").fetchall()
    assert len(contacts) == 1
    assert contacts[0]["email_normalized"] == "alice@gmail.com"
