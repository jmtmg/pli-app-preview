"""Authentification PLI - signup, login, reset, JWT + deps FastAPI.

Renomme depuis `auth_pli` le 2026-04-22 (ticket M2-unblock-auth, ADR 0007).

Modules exposes :
- passwords, jwt, tokens : couche infra (hashing, signing)
- signup, login, password_reset : use-cases applicatifs
- dependencies : helpers FastAPI (current_user, require_admin)
- deps : modele User + alias retro-compat
"""

from __future__ import annotations

from .dependencies import current_user, require_admin
from .deps import User

__all__ = ["current_user", "require_admin", "User"]
