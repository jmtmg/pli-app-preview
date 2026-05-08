"""Recherche globale via FTS5.

Sprint 4 · BE — owner : BE
    * endpoint `GET /search?q=...` retourne résultats groupés : contacts / messages / PJ
    * contrat de perf : < 300 ms pour 10k messages sur SQLite+FTS5 local
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..db import get_conn

router = APIRouter()


@router.get("", summary="Recherche globale (FTS5)")
def search(q: str = Query(..., min_length=2, max_length=200)) -> dict[str, list[dict[str, object]]]:
    """Retourne {contacts, messages, attachments}.

    Le tokenizer FTS5 utilise `unicode61 remove_diacritics 2` pour ignorer accents.
    On préfixe `q*` pour recherche par préfixe.
    """
    q_fts = " ".join(f"{tok}*" for tok in q.split() if tok)

    with get_conn() as conn:
        # Contacts — LIKE simple (les contacts ne sont pas dans FTS5 en M1)
        contacts = conn.execute(
            """SELECT id, email, display_name, company
               FROM contacts
               WHERE display_name LIKE ? OR email LIKE ? OR company LIKE ?
               ORDER BY last_msg_at DESC LIMIT 8""",
            (f"%{q}%", f"%{q}%", f"%{q}%"),
        ).fetchall()

        # Messages — FTS5 join
        messages = conn.execute(
            """SELECT m.id, m.subject, m.snippet, m.received_at, m.contact_id,
                      c.display_name, c.email
               FROM messages_fts f
               JOIN messages m ON m.rowid = f.rowid
               JOIN contacts c ON c.id = m.contact_id
               WHERE messages_fts MATCH ?
               ORDER BY rank LIMIT 20""",
            (q_fts,),
        ).fetchall()

        # Pièces jointes
        attachments = conn.execute(
            """SELECT a.id, a.filename, a.mime_type, a.contact_id, c.display_name
               FROM attachments_fts f
               JOIN attachments a ON a.rowid = f.rowid
               JOIN contacts c ON c.id = a.contact_id
               WHERE attachments_fts MATCH ?
               ORDER BY rank LIMIT 10""",
            (q_fts,),
        ).fetchall()

    return {
        "contacts": [dict(r) for r in contacts],
        "messages": [dict(r) for r in messages],
        "attachments": [dict(r) for r in attachments],
    }
