# SPDX-FileCopyrightText: 2026
# SPDX-License-Identifier: MPL-2.0

"""Add live exercise collaboration, governance, retention, and completion records."""

from alembic import op
import sqlalchemy as sa

revision = "a7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def _common_table(name: str, extra: list[sa.Column]) -> None:
    op.create_table(
        name,
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        *extra,
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def upgrade() -> None:
    _common_table("exercise_facilitators", [sa.Column("game_id", sa.String(64), nullable=False), sa.Column("user", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("permission", sa.String(32), nullable=False, server_default="facilitator")])
    _common_table("exercise_notes", [sa.Column("game_id", sa.String(64), nullable=False), sa.Column("author", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now())])
    _common_table("exercise_evidence", [sa.Column("game_id", sa.String(64), nullable=False), sa.Column("uploaded_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("storage_item_id", sa.UUID(), nullable=True), sa.Column("title", sa.String(200), nullable=False), sa.Column("question_index", sa.Integer(), nullable=True)])
    _common_table("exercise_audit_logs", [sa.Column("game_id", sa.String(64), nullable=True), sa.Column("actor", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("action", sa.String(100), nullable=False), sa.Column("details", sa.JSON(), nullable=False, server_default="{}")])
    op.create_table("data_retention_policies", sa.Column("id", sa.UUID(), primary_key=True, nullable=False), sa.Column("user", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("results_days", sa.Integer(), nullable=False, server_default="365"), sa.Column("evidence_days", sa.Integer(), nullable=False, server_default="180"), sa.Column("audit_days", sa.Integer(), nullable=False, server_default="730"), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_table("exercise_completions", sa.Column("id", sa.UUID(), primary_key=True, nullable=False), sa.Column("result", sa.UUID(), sa.ForeignKey("game_results.id", ondelete="CASCADE"), nullable=False), sa.Column("user", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("participant_name", sa.String(100), nullable=False), sa.Column("completion_code", sa.String(32), nullable=False, unique=True), sa.Column("certificate_status", sa.String(20), nullable=False, server_default="issued"), sa.Column("completed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade() -> None:
    for table in ("exercise_completions", "data_retention_policies", "exercise_audit_logs", "exercise_evidence", "exercise_notes", "exercise_facilitators"):
        op.drop_table(table)
