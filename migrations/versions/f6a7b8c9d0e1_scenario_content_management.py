# SPDX-FileCopyrightText: 2026
# SPDX-License-Identifier: MPL-2.0

"""Add durable scenario metadata and version history."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("quiz", sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("quiz", sa.Column("difficulty", sa.String(length=32), nullable=True))
    op.add_column("quiz", sa.Column("duration_minutes", sa.Integer(), nullable=True))
    op.add_column("quiz", sa.Column("framework_mappings", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("quiz", sa.Column("reusable_roles", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("quiz", sa.Column("reusable_injects", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("quiz", sa.Column("evidence_packs", sa.JSON(), nullable=False, server_default="[]"))
    op.create_table(
        "scenario_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("quiz", postgresql.UUID(as_uuid=True), sa.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("label", sa.String(length=160), nullable=False, server_default="Draft"),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("parent_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("scenario_versions")
    for column in ("evidence_packs", "reusable_injects", "reusable_roles", "framework_mappings", "duration_minutes", "difficulty", "tags"):
        op.drop_column("quiz", column)
