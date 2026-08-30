# SPDX-FileCopyrightText: 2026
# SPDX-License-Identifier: MPL-2.0

"""Add scenario reference shelf documents."""

from alembic import op
import sqlalchemy as sa

revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("quiz", sa.Column("reference_documents", sa.JSON(), nullable=False, server_default="[]"))


def downgrade() -> None:
    op.drop_column("quiz", "reference_documents")
