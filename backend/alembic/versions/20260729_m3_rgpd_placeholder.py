"""M3 RGPD placeholder — deferred cloud data-rights schema.

Revision ID: m3_rgpd_2026_07_29
Revises: 0002_m2
Create Date: 2026-07-29 09:00:00

The recovered Cowork archive contains M4 beta tables that reference this M3
revision, but the actual RGPD/exports schema is not integrated in the local v1
runtime yet. Keep a no-op revision so Alembic has a coherent graph while the
real M3 migration remains future/non-gate work documented in the PLI v1 ADR.
"""

from __future__ import annotations

revision = "m3_rgpd_2026_07_29"
down_revision = "0002_m2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    return None


def downgrade() -> None:
    return None
