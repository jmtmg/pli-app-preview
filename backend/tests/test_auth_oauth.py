"""Tests US-1.1 — flow OAuth Gmail (start + callback)."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest

from pli.api import auth as auth_module


@pytest.fixture(autouse=True)
def _clear_state_store() -> None:
    """Évite la pollution entre tests du `_STATE_STORE` module-level."""
    auth_module._STATE_STORE.clear()


# ---------------------------------------------------------------------------
# /auth/{provider}/start
# ---------------------------------------------------------------------------


def test_start_gmail_redirects_to_google_with_expected_scopes(client) -> None:
    r = client.get("/auth/gmail/start")
    assert r.status_code == 307
    loc = r.headers["location"]
    parsed = urlparse(loc)
    assert parsed.hostname == "accounts.google.com"

    qs = parse_qs(parsed.query)
    scope = qs["scope"][0]
    assert "https://www.googleapis.com/auth/gmail.readonly" in scope
    assert "https://www.googleapis.com/auth/gmail.send" in scope
    assert "https://www.googleapis.com/auth/gmail.modify" in scope
    assert "https://www.googleapis.com/auth/userinfo.email" in scope

    # Exigences Google pour obtenir un refresh_token
    assert qs["access_type"] == ["offline"]
    assert qs["prompt"] == ["consent"]
    assert qs["response_type"] == ["code"]
    assert qs["client_id"] == ["test-client-id.apps.googleusercontent.com"]

    # state doit être stocké côté serveur
    state = qs["state"][0]
    assert auth_module._STATE_STORE.get(state) == "gmail"


def test_start_rejects_unknown_provider(client) -> None:
    r = client.get("/auth/yahoo/start")
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /auth/{provider}/callback — paths d'erreur
# ---------------------------------------------------------------------------


def test_callback_missing_code_redirects_to_error(client) -> None:
    r = client.get("/auth/gmail/callback?state=xxx")
    assert r.status_code == 307
    loc = r.headers["location"]
    assert "localhost:5173/auth/error" in loc
    assert "reason=missing_code_or_state" in loc


def test_callback_invalid_state_redirects_to_error(client) -> None:
    r = client.get("/auth/gmail/callback?code=abc&state=not-registered")
    assert r.status_code == 307
    assert "reason=invalid_state" in r.headers["location"]


def test_callback_propagates_provider_error(client) -> None:
    r = client.get("/auth/gmail/callback?error=access_denied")
    assert r.status_code == 307
    assert "reason=access_denied" in r.headers["location"]


def test_callback_unsupported_provider_redirects_to_error(client) -> None:
    r = client.get("/auth/yahoo/callback?code=abc&state=xxx")
    assert r.status_code == 307
    assert "reason=unsupported_provider" in r.headers["location"]


# ---------------------------------------------------------------------------
# /auth/gmail/callback — happy path
# ---------------------------------------------------------------------------


@pytest.fixture
def stub_gmail_exchange(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    """Remplace GmailProvider.exchange_code par un stub asynchrone."""
    called: dict[str, object] = {}

    async def _fake(self, code: str) -> dict[str, object]:  # type: ignore[no-untyped-def]
        called["code"] = code
        return {
            "access_token": "ya29.fake-access",
            "refresh_token": "1//fake-refresh",
            "expires_in": 3600,
            "email": "Alice@example.COM",
            "display_name": "Alice Wonderland",
        }

    from pli.providers.gmail import GmailProvider

    monkeypatch.setattr(GmailProvider, "exchange_code", _fake)
    return called


@pytest.fixture
def stub_sync(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    """Empêche la vraie sync_account de tourner pendant le test."""
    calls: list[tuple[str, str]] = []

    async def _fake(account_id: str, kind: str = "incremental") -> dict[str, object]:
        calls.append((account_id, kind))
        return {"account_id": account_id, "kind": kind, "messages_imported": 0}

    # sync_account est importé dans pli.api.auth via `from ..sync import sync_account`
    # → on patche le nom *local* au module auth, pas la définition dans sync.service.
    monkeypatch.setattr(auth_module, "sync_account", _fake)
    return calls


def test_callback_happy_path_creates_account_and_kicks_sync(
    client, stub_gmail_exchange, stub_sync
) -> None:
    # 1. enregistrer un state valide comme si /start avait été appelé
    state = "test-state-value"
    auth_module._STATE_STORE[state] = "gmail"

    r = client.get(f"/auth/gmail/callback?code=authcode&state={state}")
    assert r.status_code == 307
    loc = r.headers["location"]
    assert loc.startswith("http://localhost:5173/?connected=")

    # 2. account persisté en DB avec email normalisé
    from pli.db import get_conn

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, provider, email, display_name, avatar_color, "
            "oauth_access, oauth_refresh, oauth_expiry, is_active "
            "FROM accounts"
        ).fetchone()
    assert row is not None
    assert row["provider"] == "gmail"
    assert row["email"] == "alice@example.com"  # normalisation lowercase
    assert row["display_name"] == "Alice Wonderland"
    assert row["is_active"] == 1
    assert row["avatar_color"] is not None

    # 3. tokens stockés chiffrés — inaccessibles en clair
    assert "ya29.fake-access" not in row["oauth_access"]
    assert "1//fake-refresh" not in row["oauth_refresh"]

    # 4. déchiffrement correct via helper
    from pli.crypto import decrypt_str

    assert decrypt_str(row["oauth_access"]) == "ya29.fake-access"
    assert decrypt_str(row["oauth_refresh"]) == "1//fake-refresh"

    # 5. sync initiale kickée avec kind="initial"
    assert len(stub_sync) == 1
    assert stub_sync[0][1] == "initial"
    assert stub_sync[0][0] == row["id"]

    # 6. redirect URL porte l'id du nouveau compte
    assert f"connected={row['id']}" in loc

    # 7. state consommé (non-rejouable)
    assert state not in auth_module._STATE_STORE


def test_callback_reconnect_preserves_refresh_when_google_omits_it(
    client, monkeypatch, stub_sync
) -> None:
    """Re-consent sans nouveau refresh_token → on garde l'ancien."""

    # 1er OAuth : avec refresh_token
    async def first_exchange(self, code: str) -> dict[str, object]:  # type: ignore[no-untyped-def]
        return {
            "access_token": "access-1",
            "refresh_token": "refresh-ORIGINAL",
            "expires_in": 3600,
            "email": "bob@example.com",
            "display_name": "Bob",
        }

    from pli.providers.gmail import GmailProvider

    monkeypatch.setattr(GmailProvider, "exchange_code", first_exchange)

    state1 = "state-1"
    auth_module._STATE_STORE[state1] = "gmail"
    client.get(f"/auth/gmail/callback?code=c1&state={state1}")

    # 2e OAuth : sans refresh_token (cas réel Google si re-consent sans prompt forcé)
    async def second_exchange(self, code: str) -> dict[str, object]:  # type: ignore[no-untyped-def]
        return {
            "access_token": "access-2",
            "refresh_token": None,
            "expires_in": 7200,
            "email": "bob@example.com",
            "display_name": "Bob Updated",
        }

    monkeypatch.setattr(GmailProvider, "exchange_code", second_exchange)

    state2 = "state-2"
    auth_module._STATE_STORE[state2] = "gmail"
    client.get(f"/auth/gmail/callback?code=c2&state={state2}")

    # Un seul compte (upsert par provider+email)
    from pli.db import get_conn

    with get_conn() as conn:
        rows = conn.execute("SELECT oauth_access, oauth_refresh FROM accounts").fetchall()
    assert len(rows) == 1

    from pli.crypto import decrypt_str

    assert decrypt_str(rows[0]["oauth_access"]) == "access-2"  # mis à jour
    assert decrypt_str(rows[0]["oauth_refresh"]) == "refresh-ORIGINAL"  # préservé


def test_callback_token_exchange_failure_redirects_to_error(client, monkeypatch, stub_sync) -> None:
    import httpx

    async def failing_exchange(self, code: str):  # type: ignore[no-untyped-def]
        req = httpx.Request("POST", "https://oauth2.googleapis.com/token")
        resp = httpx.Response(400, request=req, text='{"error":"invalid_grant"}')
        raise httpx.HTTPStatusError("400", request=req, response=resp)

    from pli.providers.gmail import GmailProvider

    monkeypatch.setattr(GmailProvider, "exchange_code", failing_exchange)

    state = "state-fail"
    auth_module._STATE_STORE[state] = "gmail"
    r = client.get(f"/auth/gmail/callback?code=bad&state={state}")

    assert r.status_code == 307
    assert "reason=token_exchange_failed" in r.headers["location"]
    # stub_sync reste vide → pas de sync déclenchée sur échec
    assert stub_sync == []
