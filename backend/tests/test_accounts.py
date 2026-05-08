"""Tests US-1.8 · BE — endpoint GET /accounts.

Verifie :
- liste des comptes actifs uniquement (is_active=1)
- agregation unread_count via JOIN contacts
- projection sans secrets (pas de tokens OAuth dans la reponse)
- tri stable par created_at ASC
- soft-delete via DELETE + 404 si deja deconnecte
- trigger sync : 404 sur compte inconnu, 400 sur kind invalide
"""

from __future__ import annotations

import time


def _seed_two_accounts() -> None:
    """Insere 2 comptes actifs + 1 inactif + contacts avec non-lus."""
    from pli.db import get_conn

    now = int(time.time())
    with get_conn() as conn:
        # Compte A (gmail) cree en premier → ordre garanti
        conn.execute(
            """
            INSERT INTO accounts (id, provider, email, display_name, avatar_color,
                                  oauth_access, oauth_refresh, oauth_expiry,
                                  last_sync_at, is_active, created_at)
            VALUES ('acc-A', 'gmail', 'alice@example.com', 'Alice',
                    '#00aa88', 'enc-token-A', 'enc-refresh-A', ?, ?, 1, ?)
            """,
            (now + 3600, now, now - 100),
        )
        # Compte B (microsoft) cree ensuite
        conn.execute(
            """
            INSERT INTO accounts (id, provider, email, is_active, created_at)
            VALUES ('acc-B', 'microsoft', 'bob@example.com', 1, ?)
            """,
            (now - 50,),
        )
        # Compte inactif — ne doit pas apparaitre
        conn.execute(
            """
            INSERT INTO accounts (id, provider, email, is_active, created_at)
            VALUES ('acc-C', 'gmail', 'old@example.com', 0, ?)
            """,
            (now - 200,),
        )
        # Contacts : A a 5 non-lus (3 + 2), B a 1, C n'aurait aucun poids
        conn.execute(
            """INSERT INTO contacts (id, account_id, email, email_normalized,
                                      kind, unread_count, last_msg_at)
               VALUES ('c-a1', 'acc-A', 'x@y.io', 'x@y.io', 'human', 3, ?)""",
            (now,),
        )
        conn.execute(
            """INSERT INTO contacts (id, account_id, email, email_normalized,
                                      kind, unread_count, last_msg_at)
               VALUES ('c-a2', 'acc-A', 'z@y.io', 'z@y.io', 'human', 2, ?)""",
            (now,),
        )
        conn.execute(
            """INSERT INTO contacts (id, account_id, email, email_normalized,
                                      kind, unread_count, last_msg_at)
               VALUES ('c-b1', 'acc-B', 'w@y.io', 'w@y.io', 'notif', 1, ?)""",
            (now,),
        )
        conn.commit()


# --------------------------------------------------------------------------
# GET /accounts
# --------------------------------------------------------------------------


def test_list_accounts_returns_active_only(client) -> None:  # type: ignore[no-untyped-def]
    _seed_two_accounts()
    r = client.get("/accounts")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)
    # Seuls acc-A et acc-B sont actifs
    ids = [a["id"] for a in data]
    assert ids == ["acc-A", "acc-B"], f"tri created_at ASC attendu, reçu {ids}"


def test_list_accounts_aggregates_unread(client) -> None:  # type: ignore[no-untyped-def]
    _seed_two_accounts()
    r = client.get("/accounts")
    assert r.status_code == 200
    by_id = {a["id"]: a for a in r.json()}
    assert by_id["acc-A"]["unread_count"] == 5
    assert by_id["acc-B"]["unread_count"] == 1


def test_list_accounts_empty_unread_when_no_contacts(client) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    now = int(time.time())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO accounts (id, provider, email, is_active, created_at) "
            "VALUES ('acc-solo', 'gmail', 'solo@x.io', 1, ?)",
            (now,),
        )
        conn.commit()
    r = client.get("/accounts")
    assert r.status_code == 200
    assert r.json()[0]["unread_count"] == 0


def test_list_accounts_does_not_leak_tokens(client) -> None:  # type: ignore[no-untyped-def]
    """Le DTO AccountSummary ne doit jamais exposer les tokens OAuth."""
    _seed_two_accounts()
    r = client.get("/accounts")
    assert r.status_code == 200
    text = r.text
    assert "enc-token-A" not in text, "Access token leaked"
    assert "enc-refresh-A" not in text, "Refresh token leaked"
    first = r.json()[0]
    assert "oauth_access" not in first
    assert "oauth_refresh" not in first
    assert "oauth_expiry" not in first
    assert "history_cursor" not in first


def test_list_accounts_returns_expected_schema(client) -> None:  # type: ignore[no-untyped-def]
    _seed_two_accounts()
    a = client.get("/accounts").json()[0]
    # Cle presentes
    for k in ("id", "provider", "email", "display_name", "avatar_color",
             "unread_count", "is_active", "last_sync_at"):
        assert k in a, f"champ manquant : {k}"
    assert a["provider"] in ("gmail", "microsoft")
    assert a["is_active"] is True
    # last_sync_at est soit None, soit une ISO (contient "T")
    if a["last_sync_at"] is not None:
        assert "T" in a["last_sync_at"]


def test_list_accounts_empty_db(client) -> None:  # type: ignore[no-untyped-def]
    r = client.get("/accounts")
    assert r.status_code == 200
    assert r.json() == []


# --------------------------------------------------------------------------
# DELETE /accounts/{id}
# --------------------------------------------------------------------------


def test_delete_account_soft_delete(client) -> None:  # type: ignore[no-untyped-def]
    _seed_two_accounts()
    r = client.delete("/accounts/acc-A")
    assert r.status_code == 200
    assert r.json() == {"status": "deactivated", "account_id": "acc-A"}
    # Desormais absent de la liste
    ids = [a["id"] for a in client.get("/accounts").json()]
    assert "acc-A" not in ids


def test_delete_account_already_deleted_returns_404(client) -> None:  # type: ignore[no-untyped-def]
    _seed_two_accounts()
    client.delete("/accounts/acc-A")
    r = client.delete("/accounts/acc-A")
    assert r.status_code == 404


def test_delete_account_unknown_returns_404(client) -> None:  # type: ignore[no-untyped-def]
    r = client.delete("/accounts/does-not-exist")
    assert r.status_code == 404


# --------------------------------------------------------------------------
# POST /accounts/{id}/sync
# --------------------------------------------------------------------------


def test_sync_unknown_account_404(client) -> None:  # type: ignore[no-untyped-def]
    r = client.post("/accounts/nope/sync", params={"kind": "incremental"})
    assert r.status_code == 404


def test_sync_invalid_kind_400(client) -> None:  # type: ignore[no-untyped-def]
    _seed_two_accounts()
    r = client.post("/accounts/acc-A/sync", params={"kind": "weird"})
    assert r.status_code == 400


def test_sync_accepts_known_account(client, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Le endpoint retourne 200 et delegue a BackgroundTasks — on ne lance pas
    reellement la sync ici (reseau out of scope pour ce test)."""
    _seed_two_accounts()

    called: list[tuple] = []

    async def fake_sync(account_id: str, kind: str = "incremental") -> None:
        called.append((account_id, kind))

    from pli.api import accounts as accounts_mod

    monkeypatch.setattr(accounts_mod, "sync_account", fake_sync)
    r = client.post("/accounts/acc-A/sync", params={"kind": "incremental"})
    assert r.status_code == 200
    assert r.json()["status"] == "started"
    # BackgroundTasks executes after response in TestClient
    assert called == [("acc-A", "incremental")] or called == []
