# SPDX-FileCopyrightText: 2026
#
# SPDX-License-Identifier: MPL-2.0

"""Added role_descriptions and teams to quiz

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("quiz", sa.Column("role_descriptions", sa.JSON(), nullable=True))
    op.add_column("quiz", sa.Column("teams", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("quiz", "teams")
    op.drop_column("quiz", "role_descriptions")