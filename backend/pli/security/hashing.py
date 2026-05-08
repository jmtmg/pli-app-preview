"""Hashing utilities RGPD-safe."""

from __future__ import annotations

import hashlib
import hmac
import os


def _salt() -> bytes:
    salt = os.environ.get("PLI_USER_HASH_SALT")
    if not salt:
        raise RuntimeError("PLI_USER_HASH_SALT non configuré — jamais de fallback en prod.")
    return salt.encode("utf-8")


def user_hash(user_id: int) -> str:
    """Hash HMAC-SHA256 du user_id pour les logs et feedback RGPD-safe."""
    mac = hmac.new(_salt(), msg=str(user_id).encode("utf-8"), digestmod=hashlib.sha256)
    return mac.hexdigest()
