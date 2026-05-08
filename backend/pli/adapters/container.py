"""Container d'adapters — unique endroit qui lit `settings.mode`.

Le container est construit au démarrage (`init_container()`) et exposé via
les providers `get_storage()`, `get_search()`, etc. à utiliser comme
dépendances FastAPI.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import settings
from .base import (
    CryptoAdapter,
    Principal,
    PrincipalResolver,
    SearchAdapter,
    SettingsStore,
    StorageAdapter,
)


@dataclass
class Container:
    storage: StorageAdapter
    search: SearchAdapter
    principal_resolver: PrincipalResolver
    settings_store: SettingsStore
    crypto: CryptoAdapter


_container: Container | None = None


def init_container() -> Container:
    """Construit les adapters selon `settings.mode`. Appelé dans `lifespan`."""
    global _container
    if settings.mode == "local":
        from .local import (
            LocalCryptoAdapter,
            LocalSearchAdapter,
            LocalSettingsStore,
            LocalStorageAdapter,
            local_principal_resolver,
        )

        _container = Container(
            storage=LocalStorageAdapter(),
            search=LocalSearchAdapter(),
            principal_resolver=local_principal_resolver,
            settings_store=LocalSettingsStore(),
            crypto=LocalCryptoAdapter(),
        )
    else:
        from .cloud import (
            CloudCryptoAdapter,
            CloudSearchAdapter,
            CloudSettingsStore,
            CloudStorageAdapter,
            cloud_principal_resolver,
        )

        _container = Container(
            storage=CloudStorageAdapter(),
            search=CloudSearchAdapter(),
            principal_resolver=cloud_principal_resolver,
            settings_store=CloudSettingsStore(),
            crypto=CloudCryptoAdapter(),
        )
    return _container


def _c() -> Container:
    if _container is None:
        init_container()
    assert _container is not None
    return _container


# ---- FastAPI dependency providers ----


def get_storage() -> StorageAdapter:
    return _c().storage


def get_search() -> SearchAdapter:
    return _c().search


def get_settings_store() -> SettingsStore:
    return _c().settings_store


def get_crypto() -> CryptoAdapter:
    return _c().crypto


async def get_principal(request) -> Principal:  # type: ignore[no-untyped-def]
    """Résout le principal via l'adapter configuré."""
    return await _c().principal_resolver(request)


def get_principal_resolver() -> PrincipalResolver:
    return _c().principal_resolver


# Permet aux tests d'injecter un container synthétique.
def override_container(container: Container) -> None:
    global _container
    _container = container
