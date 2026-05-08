"""Deterministic local demo data for PLI.

This module never contacts email providers and never stores real secrets. It is
only used in local/demo mode so the recovered project can be opened, tested and
shown without Gmail/Microsoft credentials.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

from .db import get_conn

DEMO_ACCOUNT_ID = "demo-account-gmail"


@dataclass(frozen=True)
class DemoContact:
    id: str
    email: str
    display_name: str
    company: str | None
    role: str | None
    kind: str = "human"
    is_pinned: int = 0
    pinned_order: int | None = None


CONTACTS: tuple[DemoContact, ...] = (
    DemoContact(
        id="demo-contact-alice",
        email="alice.martin@demo-pli.com",
        display_name="Alice Martin",
        company="JMJ Consulting",
        role="Direction opérations",
        is_pinned=1,
        pinned_order=1,
    ),
    DemoContact(
        id="demo-contact-banque",
        email="notifications@demo-bank.com",
        display_name="Banque — notifications",
        company="Banque Demo",
        role="Alertes automatiques",
        kind="notif",
    ),
    DemoContact(
        id="demo-contact-test",
        email="test.pli@demo-pli.com",
        display_name="Adresse test PLI",
        company="PLI Demo",
        role="Boîte de test locale",
        is_pinned=1,
        pinned_order=2,
    ),
    DemoContact(
        id="demo-contact-legal",
        email="maitre.durand@cabinet-durand.fr",
        display_name="Me Durand",
        company="Cabinet Durand",
        role="Conseil juridique",
    ),
)


def seed_demo_data(reset: bool = False) -> dict[str, int | bool]:
    """Seed a small local mailbox.

    The operation is idempotent by default. With ``reset=True`` only rows using
    the deterministic ``demo-*`` ids/provider ids are removed first; real user
    data is left untouched.
    """
    now = int(time.time())
    with get_conn() as conn:
        if reset:
            conn.execute("DELETE FROM attachments WHERE id LIKE 'demo-%'")
            conn.execute("DELETE FROM messages WHERE id LIKE 'demo-%' OR provider_id LIKE 'demo-%'")
            conn.execute("DELETE FROM contacts WHERE id LIKE 'demo-%'")
            conn.execute("DELETE FROM accounts WHERE id = ?", (DEMO_ACCOUNT_ID,))

        conn.execute(
            """
            INSERT OR IGNORE INTO accounts(
                id, provider, email, display_name, oauth_access, oauth_refresh,
                oauth_expiry, history_cursor, signature, avatar_color,
                last_sync_at, is_active, created_at
            ) VALUES (?, 'gmail', ?, ?, '', '', NULL, 'demo-cursor', ?, ?, ?, 1, ?)
            """,
            (
                DEMO_ACCOUNT_ID,
                "demo@pli-app.fr",
                "Boîte demo PLI",
                "—\nJMJ",
                "#c9a47d",
                now,
                now - 60,
            ),
        )

        for idx, c in enumerate(CONTACTS):
            conn.execute(
                """
                INSERT OR IGNORE INTO contacts(
                    id, account_id, email, email_normalized, display_name,
                    company, role, notes, is_muted, is_pinned, pinned_order,
                    kind, last_msg_at, unread_count, has_attachments, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, 0, 0, ?)
                """,
                (
                    c.id,
                    DEMO_ACCOUNT_ID,
                    c.email,
                    c.email.lower(),
                    c.display_name,
                    c.company,
                    c.role,
                    "Contact de démonstration local — aucune donnée réelle.",
                    c.is_pinned,
                    c.pinned_order,
                    c.kind,
                    now - (idx * 3600),
                    now - (idx * 3600),
                ),
            )

        messages = [
            (
                "demo-msg-001",
                "demo-contact-alice",
                "in",
                "Point PLI",
                "Voici la synthèse du jour : le MVP local doit démarrer sans credentials.",
                "alice.martin@demo-pli.com",
                "Alice Martin",
                now - 7200,
                0,
            ),
            (
                "demo-msg-002",
                "demo-contact-alice",
                "out",
                "Re: Point PLI",
                "Bien reçu. Je stabilise d’abord le backend, le frontend et le parcours local.",
                "demo@pli-app.fr",
                "Boîte demo PLI",
                now - 6900,
                1,
            ),
            (
                "demo-msg-003",
                "demo-contact-banque",
                "in",
                "Notification compte",
                "Votre relevé mensuel de démonstration est disponible.",
                "notifications@demo-bank.com",
                "Banque — notifications",
                now - 3600,
                0,
            ),
            (
                "demo-msg-005",
                "demo-contact-test",
                "in",
                "Adresse de test PLI",
                "Cette adresse de test locale sert à valider les conversations et le composer sans vrai compte email.",
                "test.pli@demo-pli.com",
                "Adresse test PLI",
                now - 2400,
                0,
            ),
            (
                "demo-msg-004",
                "demo-contact-legal",
                "in",
                "CGU / confidentialité",
                "Penser à finaliser les mentions légales avant bêta publique.",
                "maitre.durand@cabinet-durand.fr",
                "Me Durand",
                now - 1200,
                1,
            ),
        ]
        for mid, contact_id, direction, subject, body, from_email, from_name, ts, is_read in messages:
            conn.execute(
                """
                INSERT OR IGNORE INTO messages(
                    id, account_id, contact_id, provider_id, thread_id, direction,
                    subject, snippet, body_text, body_html, from_email, from_name,
                    to_emails, cc_emails, received_at, is_read, is_starred,
                    has_attachments, raw_headers, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, '[]', ?, ?, 0, 0, '', ?)
                """,
                (
                    mid,
                    DEMO_ACCOUNT_ID,
                    contact_id,
                    f"demo-provider-{mid}",
                    f"thread-{contact_id}",
                    direction,
                    subject,
                    body[:140],
                    body,
                    from_email,
                    from_name,
                    json.dumps(["demo@pli-app.fr"] if direction == "in" else [from_email]),
                    ts,
                    is_read,
                    ts,
                ),
            )

        conn.execute(
            """
            INSERT OR IGNORE INTO attachments(
                id, message_id, contact_id, filename, mime_type,
                size_bytes, sha256, ocr_text, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "demo-att-001",
                "demo-msg-001",
                "demo-contact-alice",
                "mvp-local-demo.pdf",
                "application/pdf",
                42_000,
                "demo-attachment-sha256",
                "MVP local demo sans credentials réels",
                now - 7100,
            ),
        )

        conn.execute(
            """
            UPDATE contacts
            SET last_msg_at = COALESCE((
                    SELECT MAX(received_at) FROM messages WHERE messages.contact_id = contacts.id
                ), last_msg_at),
                unread_count = COALESCE((
                    SELECT COUNT(*) FROM messages
                    WHERE messages.contact_id = contacts.id
                      AND messages.direction = 'in'
                      AND messages.is_read = 0
                ), 0),
                has_attachments = COALESCE((
                    SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END FROM attachments
                    WHERE attachments.contact_id = contacts.id
                ), 0)
            WHERE id LIKE 'demo-%'
            """
        )
        conn.commit()

        counts = {
            "accounts": conn.execute("SELECT COUNT(*) FROM accounts WHERE id LIKE 'demo-%'").fetchone()[0],
            "contacts": conn.execute("SELECT COUNT(*) FROM contacts WHERE id LIKE 'demo-%'").fetchone()[0],
            "messages": conn.execute("SELECT COUNT(*) FROM messages WHERE id LIKE 'demo-%'").fetchone()[0],
            "attachments": conn.execute("SELECT COUNT(*) FROM attachments WHERE id LIKE 'demo-%'").fetchone()[0],
        }
    return {"ok": True, "reset": reset, **counts}


def seed_local_demo(reset: bool = True) -> dict[str, int]:
    """Backward-compatible helper used by ``pli.api.demo``.

    Returns only the numeric counters expected by the original demo router.
    """
    result = seed_demo_data(reset=reset)
    return {
        "accounts": int(result["accounts"]),
        "contacts": int(result["contacts"]),
        "messages": int(result["messages"]),
        "attachments": int(result.get("attachments", 0)),
    }
