"""Hashing Argon2id — paramètres OWASP 2025.

OWASP recommande : m=19MiB, t=2, p=1 (minimum).
On prend m=32MiB, t=3, p=2 pour marge de sécurité (coût ~0.15 s/hash sur serveur moyen).
"""

from __future__ import annotations

import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=32 * 1024,  # 32 MiB
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


class PasswordPolicyError(ValueError):
    pass


# Politique minimale : >= 12 chars, au moins 3 catégories parmi {lower, upper, digit, symbol}.
# (On ne remplace pas zxcvbn — on le complète en entrée de signup.)
_CATEGORIES = (
    re.compile(r"[a-z]"),
    re.compile(r"[A-Z]"),
    re.compile(r"[0-9]"),
    re.compile(r"[^\w\s]"),
)


def validate_policy(password: str) -> None:
    if len(password) < 12:
        raise PasswordPolicyError("password_too_short_min_12")
    matched = sum(1 for rx in _CATEGORIES if rx.search(password))
    if matched < 3:
        raise PasswordPolicyError("password_needs_3_categories")


def hash_password(password: str) -> str:
    validate_policy(password)
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        _hasher.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(hashed: str) -> bool:
    """True si l'algo/params ont évolué et qu'il faut re-hasher au prochain login."""
    return _hasher.check_needs_rehash(hashed)
