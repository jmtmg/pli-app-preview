"""Module tenancy — isolation stricte multi-tenant (ADR-0002)."""

from .context import (
    TenantContextMiddleware,
    current_tenant_id,
    require_tenant,
    set_current_tenant,
)
from .repository import TenantIsolationError, TenantScopedRepository

__all__ = [
    "TenantContextMiddleware",
    "current_tenant_id",
    "require_tenant",
    "set_current_tenant",
    "TenantScopedRepository",
    "TenantIsolationError",
]
