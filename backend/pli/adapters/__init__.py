"""Pattern adapters — isolation Local vs Cloud (ADR-0001).

L'application ne doit jamais lire `settings.mode` directement, sauf dans
`container.py`. Tout le code métier passe par les interfaces définies ici.

Usage FastAPI :

    from fastapi import Depends
    from pli.adapters import get_storage, StorageAdapter

    @router.get("/{id}")
    async def download(id: str, storage: StorageAdapter = Depends(get_storage)):
        ...
"""

from .base import (
    CryptoAdapter,
    PrincipalResolver,
    SearchAdapter,
    SettingsStore,
    StorageAdapter,
)
from .container import (
    get_crypto,
    get_principal_resolver,
    get_search,
    get_settings_store,
    get_storage,
    init_container,
)

__all__ = [
    "StorageAdapter",
    "SearchAdapter",
    "PrincipalResolver",
    "SettingsStore",
    "CryptoAdapter",
    "get_storage",
    "get_search",
    "get_principal_resolver",
    "get_settings_store",
    "get_crypto",
    "init_container",
]
