"""Dépendances FastAPI pour l'authentification (compat M2 / M3 / M4).

Utilisation type dans un router :

    from fastapi import APIRouter, Depends
    from pli.auth.dependencies import current_user, require_admin

    @router.get("/me")
    def me(user = Depends(current_user)):
        ...

    @router.post("/admin/purge")
    def purge(user = Depends(require_admin)):
        ...

Implémentation :
- `current_user` décode le JWT access token présent dans l'header
  `Authorization: Bearer <token>` (cf. `pli.auth.jwt`).
- `require_admin` est un wrapper qui lève 403 si `user.is_admin` est faux.
- Le `User` renvoyé est défini dans `pli.auth.deps` (modèle minimal utilisé
  en M2) ; M3/M4 peuvent utiliser leurs propres modèles ORM tant qu'ils
  respectent les attributs `id`, `email`, `plan`, `is_admin`.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from .deps import User
from .jwt import TokenError, decode_access_token


async def current_user(request: Request) -> User:
    """Extrait l'utilisateur courant depuis le JWT access token."""
    auth_header = request.headers.get("authorization") or ""
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_bearer_token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ", 1)[1].strip()
    try:
        claim = decode_access_token(token)
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e) or "invalid_token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return User(
        id=claim.id,
        email=claim.email,
        plan=claim.plan,
        is_admin=False,
    )


async def require_admin(user: User = Depends(current_user)) -> User:
    """Dépendance admin-only (403 sinon)."""
    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin_required",
        )
    return user
