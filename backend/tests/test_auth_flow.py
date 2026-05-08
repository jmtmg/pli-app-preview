"""Tests bout-en-bout du parcours auth PLI."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


SIGNUP_PAYLOAD = {
    "email": "user@test.invalid",
    "password": "Sup3rStrong!Pass1",
    "accept_terms": True,
}


async def test_signup_then_verify_then_login(client: AsyncClient, mail_outbox):
    r = await client.post("/auth/signup", json=SIGNUP_PAYLOAD)
    assert r.status_code == 201, r.text
    assert mail_outbox[-1]["template"] == "verification"
    token = mail_outbox[-1]["context"]["token"]

    # Login refusé tant que non vérifié
    r2 = await client.post(
        "/auth/login",
        json={
            "email": SIGNUP_PAYLOAD["email"],
            "password": SIGNUP_PAYLOAD["password"],
        },
    )
    assert r2.status_code == 403
    assert r2.json()["detail"] == "email_not_verified"

    # Verify
    r3 = await client.post("/auth/verify", json={"token": token})
    assert r3.status_code == 200
    assert r3.json()["verified"] is True

    # Login OK
    r4 = await client.post(
        "/auth/login",
        json={
            "email": SIGNUP_PAYLOAD["email"],
            "password": SIGNUP_PAYLOAD["password"],
        },
    )
    assert r4.status_code == 200
    body = r4.json()
    assert body["access_token"]
    assert "pli_refresh" in r4.cookies


async def test_signup_duplicate_email(client: AsyncClient):
    r1 = await client.post("/auth/signup", json=SIGNUP_PAYLOAD)
    assert r1.status_code == 201
    r2 = await client.post("/auth/signup", json=SIGNUP_PAYLOAD)
    assert r2.status_code == 409


async def test_password_policy_enforced(client: AsyncClient):
    r = await client.post(
        "/auth/signup",
        json={
            "email": "weak@test.invalid",
            "password": "weak",
            "accept_terms": True,
        },
    )
    assert r.status_code == 422


async def test_refresh_rotation_and_replay_detection(client: AsyncClient, verified_user):
    # Login
    r = await client.post(
        "/auth/login",
        json={
            "email": verified_user["email"],
            "password": verified_user["password"],
        },
    )
    assert r.status_code == 200
    refresh1 = r.cookies["pli_refresh"]

    # Premier refresh : OK, rotation effectuée
    r2 = await client.post("/auth/refresh", cookies={"pli_refresh": refresh1})
    assert r2.status_code == 200
    refresh2 = r2.cookies["pli_refresh"]
    assert refresh2 != refresh1

    # Réutilisation de refresh1 (token déjà rotaté) → détection vol
    r3 = await client.post("/auth/refresh", cookies={"pli_refresh": refresh1})
    assert r3.status_code == 401

    # Et refresh2 doit aussi être désormais invalide (toutes sessions révoquées)
    r4 = await client.post("/auth/refresh", cookies={"pli_refresh": refresh2})
    assert r4.status_code == 401


async def test_password_reset_flow(client: AsyncClient, verified_user, mail_outbox):
    r = await client.post(
        "/auth/password-reset/request",
        json={"email": verified_user["email"]},
    )
    assert r.status_code == 200
    assert mail_outbox[-1]["template"] == "password_reset"
    token = mail_outbox[-1]["context"]["token"]

    r2 = await client.post(
        "/auth/password-reset/confirm",
        json={
            "token": token,
            "new_password": "BrandNewPassw0rd!",
        },
    )
    assert r2.status_code == 200

    # L'ancien password ne marche plus
    r3 = await client.post(
        "/auth/login",
        json={
            "email": verified_user["email"],
            "password": verified_user["password"],
        },
    )
    assert r3.status_code == 401

    # Le nouveau marche
    r4 = await client.post(
        "/auth/login",
        json={
            "email": verified_user["email"],
            "password": "BrandNewPassw0rd!",
        },
    )
    assert r4.status_code == 200


async def test_password_reset_silent_on_unknown_email(client: AsyncClient):
    r = await client.post(
        "/auth/password-reset/request",
        json={"email": "ghost@nope.invalid"},
    )
    # Doit toujours répondre 200 — pas de fuite d'info
    assert r.status_code == 200
    assert r.json()["sent"] is True


async def test_logout_revokes_session(client: AsyncClient, verified_user):
    r = await client.post(
        "/auth/login",
        json={
            "email": verified_user["email"],
            "password": verified_user["password"],
        },
    )
    refresh = r.cookies["pli_refresh"]
    access = r.json()["access_token"]

    # Logout
    rl = await client.post(
        "/auth/logout",
        cookies={"pli_refresh": refresh},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert rl.status_code == 200

    # Refresh ne marche plus
    r2 = await client.post("/auth/refresh", cookies={"pli_refresh": refresh})
    assert r2.status_code == 401
