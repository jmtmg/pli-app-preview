"""Tests — émission + vérification de licences Ed25519."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pli.licensing.local_key import (
    LICENSE_VERSION,
    generate_keypair,
    issue_local_license,
    user_hash_for,
    verify_license,
)


@pytest.fixture
def keypair():
    return generate_keypair()


def test_roundtrip_signing(keypair):
    sk, pk = keypair
    blob = issue_local_license(
        email="alice@example.com",
        plan="plus_yearly",
        valid_until=datetime.now(tz=UTC) + timedelta(days=365),
        signing_key_b64=sk,
    )
    lic = verify_license(blob, public_key_b64=pk)
    assert lic.plan == "plus_yearly"
    assert lic.version == LICENSE_VERSION
    assert lic.user_hash == user_hash_for("alice@example.com")


def test_email_mismatch_rejected(keypair):
    sk, pk = keypair
    blob = issue_local_license(
        email="alice@example.com",
        plan="plus_monthly",
        valid_until=None,
        signing_key_b64=sk,
    )
    with pytest.raises(ValueError, match="autre adresse email"):
        verify_license(blob, public_key_b64=pk, expected_email="mallory@example.com")


def test_tampered_signature_rejected(keypair):
    sk, pk = keypair
    blob = issue_local_license(
        email="alice@example.com",
        plan="plus_yearly",
        valid_until=None,
        signing_key_b64=sk,
    )
    # Flip un caractère de la signature
    blob["sig"] = blob["sig"][:-2] + ("AA" if blob["sig"][-2:] != "AA" else "BB")
    with pytest.raises(ValueError):
        verify_license(blob, public_key_b64=pk)


def test_tampered_payload_rejected(keypair):
    sk, pk = keypair
    blob = issue_local_license(
        email="alice@example.com",
        plan="plus_monthly",
        valid_until=None,
        signing_key_b64=sk,
    )
    import base64
    import json

    pad = "=" * (-len(blob["payload"]) % 4)
    raw = json.loads(base64.urlsafe_b64decode(blob["payload"] + pad))
    raw["plan"] = "plus_yearly"  # escalade de privilège
    tampered = (
        base64.urlsafe_b64encode(json.dumps(raw, separators=(",", ":"), sort_keys=True).encode())
        .decode()
        .rstrip("=")
    )
    with pytest.raises(ValueError):
        verify_license({"payload": tampered, "sig": blob["sig"]}, public_key_b64=pk)


def test_expired_license_flag(keypair):
    sk, pk = keypair
    blob = issue_local_license(
        email="a@b.c",
        plan="plus_trial",
        valid_until=datetime.now(tz=UTC) - timedelta(days=1),
        signing_key_b64=sk,
    )
    lic = verify_license(blob, public_key_b64=pk)
    assert lic.is_expired() is True


def test_cross_keypair_fails(keypair):
    sk1, _ = keypair
    _, pk2 = generate_keypair()
    blob = issue_local_license(
        email="a@b.c", plan="plus_yearly", valid_until=None, signing_key_b64=sk1
    )
    with pytest.raises(ValueError):
        verify_license(blob, public_key_b64=pk2)
