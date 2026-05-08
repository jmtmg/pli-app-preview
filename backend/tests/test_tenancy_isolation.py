"""Test critique d'isolation multi-tenant (ADR-0002).

Crée 2 utilisateurs, insère des données pour chacun, puis tente
des accès croisés sur toutes les routes API. Aucun ne doit aboutir.

Bloquant CI : si un seul cas échoue, le PR ne passe pas.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def two_users(client: AsyncClient):
    """Crée 2 users vérifiés A et B, retourne leurs tokens."""
    from pli.auth.jwt import issue_access_token
    from pli.auth.signup import create_user

    user_a = await create_user(email="alice@test.invalid", password="StrongPassword!1234")
    user_b = await create_user(email="bob@test.invalid", password="StrongPassword!1234")

    return {
        "a": {
            "user_id": user_a.id,
            "headers": {"Authorization": f"Bearer {issue_access_token(user_a)}"},
        },
        "b": {
            "user_id": user_b.id,
            "headers": {"Authorization": f"Bearer {issue_access_token(user_b)}"},
        },
    }


@pytest.fixture
async def alice_account(client: AsyncClient, two_users):
    """Compte mail créé par Alice."""
    r = await client.post(
        "/accounts",
        json={"provider": "gmail", "email": "alice@gmail.test", "display_name": "Alice"},
        headers=two_users["a"]["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()


# ---------- Routes — Alice crée, Bob ne doit jamais voir ----------

ROUTES_GET = [
    "/accounts/{account_id}",
    "/accounts/{account_id}/sync-status",
    "/conversations?account_id={account_id}",
    "/messages?account_id={account_id}",
    "/contacts?account_id={account_id}",
    "/search?q=test&account_id={account_id}",
    "/billing/subscription",  # Bob lit son propre, ne doit pas voir Alice
]

ROUTES_MUTATE = [
    ("DELETE", "/accounts/{account_id}"),
    ("POST", "/accounts/{account_id}/sync"),
    ("PUT", "/accounts/{account_id}", {"display_name": "PWNED"}),
]


@pytest.mark.parametrize("route", ROUTES_GET)
async def test_bob_cannot_read_alice(client, two_users, alice_account, route):
    url = route.format(account_id=alice_account["id"])
    r = await client.get(url, headers=two_users["b"]["headers"])
    assert r.status_code in (403, 404), (
        f"INCIDENT TENANT : route {url} renvoie {r.status_code} pour Bob alors "
        f"que la ressource appartient à Alice. Body: {r.text[:200]}"
    )


@pytest.mark.parametrize(
    "method,route,payload",
    [
        ("DELETE", "/accounts/{account_id}", None),
        ("POST", "/accounts/{account_id}/sync", None),
        ("PUT", "/accounts/{account_id}", {"display_name": "PWNED"}),
    ],
)
async def test_bob_cannot_mutate_alice(client, two_users, alice_account, method, route, payload):
    url = route.format(account_id=alice_account["id"])
    body = payload
    r = await client.request(
        method,
        url,
        headers=two_users["b"]["headers"],
        json=body,
    )
    assert r.status_code in (403, 404), (
        f"INCIDENT TENANT : {method} {url} renvoie {r.status_code} pour Bob. Body: {r.text[:200]}"
    )

    # Vérification finale : la ressource d'Alice n'a pas été modifiée
    verif = await client.get(
        f"/accounts/{alice_account['id']}",
        headers=two_users["a"]["headers"],
    )
    assert verif.status_code == 200
    if body and "display_name" in body:
        assert verif.json()["display_name"] != "PWNED", (
            "Mutation Bob a affecté Alice — INCIDENT CRITIQUE"
        )


# ---------- Test direct du repository (couche 1) ----------


async def test_repository_refuses_sql_without_user_id():
    """La base TenantScopedRepository refuse un SELECT sans clause user_id."""
    from pli.tenancy.repository import TenantIsolationError, TenantScopedRepository

    repo = TenantScopedRepository(tenant_id="alice")
    with pytest.raises(TenantIsolationError):
        await repo.fetch_all("SELECT * FROM messages")


# ---------- Test middleware (couche 2) ----------


async def test_no_token_no_access(client):
    """Sans Authorization header, toutes les routes protégées renvoient 401."""
    for url in ("/accounts", "/conversations", "/messages", "/contacts"):
        r = await client.get(url)
        assert r.status_code == 401, f"{url} a renvoyé {r.status_code} sans token"


# ---------- Test RLS PostgreSQL (couche 3 — skipif sqlite) ----------


@pytest.mark.skipif("settings.mode != 'cloud'")
async def test_rls_blocks_query_without_set_config():
    """Sans set_config('pli.current_tenant'), PG retourne 0 ligne malgré data."""
    from pli.db import get_pg_conn

    async with get_pg_conn(tenant_id=None) as conn:  # pas de set_config
        rows = await conn.fetch("SELECT * FROM messages")
        assert rows == [], "RLS désactivée : la requête sans tenant_set retourne des lignes"
