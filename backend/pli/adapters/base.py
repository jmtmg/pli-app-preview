"""Interfaces abstraites des adapters.

Toute impl concrète (Local / Cloud) hérite d'une des classes ici et vit dans
`adapters/local.py` ou `adapters/cloud.py`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

# ---------------------------------------------------------------------------
# Exceptions métier communes
# ---------------------------------------------------------------------------


class AdapterError(Exception):
    """Base de toutes les erreurs adapters."""


class StorageNotFound(AdapterError):
    """Objet demandé inexistant dans le backend de stockage."""


class StorageQuotaExceeded(AdapterError):
    """Tenant a dépassé son quota (Cloud uniquement)."""


class TenantIsolationError(AdapterError):
    """Tentative d'accès à une ressource hors du tenant courant — incident sécurité."""


# ---------------------------------------------------------------------------
# Storage (pièces jointes)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StoredObject:
    key: str  # "att/<tenant_id>/<sha256>"
    size_bytes: int
    content_type: str | None
    sha256: str


class StorageAdapter(ABC):
    """Stockage binaire des pièces jointes.

    Le `tenant_id` est un argument obligatoire — les impls sont tenues de
    préfixer les clés par le tenant pour garantir l'isolation.
    """

    @abstractmethod
    async def put(
        self,
        *,
        tenant_id: str,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> StoredObject: ...

    @abstractmethod
    async def get(self, *, tenant_id: str, key: str) -> bytes: ...

    @abstractmethod
    async def delete(self, *, tenant_id: str, key: str) -> None: ...

    @abstractmethod
    async def presigned_url(
        self,
        *,
        tenant_id: str,
        key: str,
        ttl_seconds: int = 300,
    ) -> str: ...

    @abstractmethod
    async def iter_tenant(self, *, tenant_id: str) -> AsyncIterator[StoredObject]: ...


# ---------------------------------------------------------------------------
# Full-text search
# ---------------------------------------------------------------------------


class SearchAdapter(ABC):
    @abstractmethod
    async def index_message(
        self, *, tenant_id: str, message_id: str, subject: str, body: str, from_: str
    ) -> None: ...

    @abstractmethod
    async def query(self, *, tenant_id: str, q: str, limit: int = 50) -> list[dict]: ...

    @abstractmethod
    async def delete_message(self, *, tenant_id: str, message_id: str) -> None: ...


# ---------------------------------------------------------------------------
# Principal resolver (qui est l'utilisateur appelant)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Principal:
    """Identité résolue de l'appelant courant.

    En Local : principal fixe issu de l'OS user, tenant_id == "local".
    En Cloud : extrait du JWT access token (cf. auth.jwt).
    """

    tenant_id: str
    user_id: str  # identique à tenant_id en Cloud, "local" en Local
    plan: str  # "free" | "plus_trial" | "plus_monthly" | "plus_yearly"
    email: str | None = None


class PrincipalResolver(Protocol):
    """Callable extrayant le Principal d'une requête HTTP."""

    async def __call__(self, request) -> Principal: ...  # type: ignore[no-untyped-def]


# ---------------------------------------------------------------------------
# Settings store
# ---------------------------------------------------------------------------


class SettingsStore(ABC):
    @abstractmethod
    async def get(self, *, tenant_id: str, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, *, tenant_id: str, key: str, value: str) -> None: ...

    @abstractmethod
    async def delete(self, *, tenant_id: str, key: str) -> None: ...


# ---------------------------------------------------------------------------
# Crypto at rest (chiffrement des tokens OAuth, PJ côté Local)
# ---------------------------------------------------------------------------


class CryptoAdapter(ABC):
    @abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes: ...

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes: ...
