# SPDX-FileCopyrightText: 2025
#
# SPDX-License-Identifier: MPL-2.0

"""Added injects, facilitator notes, discussion timer, and situation room

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import ormar


# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add injects JSON column to quiz table
    op.add_column("quiz", sa.Column("injects", sa.JSON(), nullable=True))

    # Add injects_log and situation_log JSON columns to game_results table
    op.add_column("game_results", sa.Column("injects_log", sa.JSON(), nullable=True))
    op.add_column("game_results", sa.Column("situation_log", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("game_results", "situation_log")
    op.drop_column("game_results", "injects_log")
    op.drop_column("quiz", "injects")
