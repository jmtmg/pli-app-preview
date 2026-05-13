"""M4 beta tables: waitlist, invitations, feedback, nps

Revision ID: m4_beta_2026_08_12
Revises: m3_rgpd_2026_07_29
Create Date: 2026-08-12 09:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "m4_beta_2026_08_12"
down_revision = "m3_rgpd_2026_07_29"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "waitlist",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("motivation", sa.String(280), nullable=True),
        sa.Column("source", sa.String(40), nullable=True, comment="landing, social, referral"),
        sa.Column(
            "segment",
            sa.String(20),
            nullable=False,
            server_default="unknown",
            comment="gmail_only, ms_only, mixed, non_tech, unknown",
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_waitlist_segment", "waitlist", ["segment"])
    op.create_index("ix_waitlist_invited", "waitlist", ["invited_at"])

    op.create_table(
        "invitations",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("batch_number", sa.Integer, nullable=False),
        sa.Column("waitlist_id", sa.BigInteger, sa.ForeignKey("waitlist.id"), nullable=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("redeemed_by_user_id", sa.String, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_invitations_batch", "invitations", ["batch_number"])
    op.create_index("ix_invitations_email", "invitations", ["email"])

    op.create_table(
        "feedback_submissions",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("user_id_hash", sa.String(64), nullable=True, comment="sha256(user_id + salt), null si anonyme"),
        sa.Column("kind", sa.String(20), nullable=False, comment="nps, bug, suggestion, other"),
        sa.Column("score", sa.Integer, nullable=True, comment="0-10, rempli si kind=nps"),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("app_version", sa.String(20), nullable=True),
        sa.Column("platform", sa.String(20), nullable=True, comment="pwa-mobile, pwa-desktop"),
        sa.Column("days_since_signup", sa.Integer, nullable=True),
        sa.Column("batch_number", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_feedback_kind", "feedback_submissions", ["kind"])
    op.create_index("ix_feedback_created", "feedback_submissions", ["created_at"])
    op.create_index("ix_feedback_batch", "feedback_submissions", ["batch_number"])

    op.create_table(
        "activation_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("event", sa.String(40), nullable=False, comment="signup, email_verified, oauth_connected, first_sync, tour_completed, first_send"),
        sa.Column("batch_number", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_activation_user_event", "activation_events", ["user_id", "event"])
    op.create_index("ix_activation_batch", "activation_events", ["batch_number"])


def downgrade() -> None:
    op.drop_index("ix_activation_batch", table_name="activation_events")
    op.drop_index("ix_activation_user_event", table_name="activation_events")
    op.drop_table("activation_events")

    op.drop_index("ix_feedback_batch", table_name="feedback_submissions")
    op.drop_index("ix_feedback_created", table_name="feedback_submissions")
    op.drop_index("ix_feedback_kind", table_name="feedback_submissions")
    op.drop_table("feedback_submissions")

    op.drop_index("ix_invitations_email", table_name="invitations")
    op.drop_index("ix_invitations_batch", table_name="invitations")
    op.drop_table("invitations")

    op.drop_index("ix_waitlist_invited", table_name="waitlist")
    op.drop_index("ix_waitlist_segment", table_name="waitlist")
    op.drop_table("waitlist")
