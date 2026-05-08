"""Modèle `User` léger + alias `current_user` (compat M3 OCR).

Historique :
- M2 introduit `pli.auth.dependencies.current_user`.
- M3 (module OCR) importait `from pli.auth.deps import User, current_user`
  avant que le package ait été renommé. On conserve ce chemin pour
  minimiser la surface de diff côté M3.

`User` est un dataclass neutre, indépendant d'un ORM particulier :
- en M2 (asyncpg), il est construit depuis le claim JWT ;
- en M3/M4 (SQLAlchemy), une surcharge locale peut hériter de ce type.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    id: str
    email: str
    plan: str = "free"
    is_admin: bool = False


# Alias rétro-compatible : `from pli.auth.deps import current_user`.
# On l'importe paresseusement pour éviter une boucle d'import avec
# `dependencies.py` → `deps.py` (qui importerait à son tour
# `dependencies.py` pour `current_user`).
def current_user(*args, **kwargs):  # pragma: no cover — proxy
    from .dependencies import current_user as _impl

    return _impl(*args, **kwargs)
