# SPDX-FileCopyrightText: 2025
#
# SPDX-License-Identifier: MPL-2.0

"""Added tabletop exercise support

Revision ID: a1b2c3d4e5f6
Revises: 9d7fa2e6b24c
Create Date: 2026-04-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import ormar


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "9d7fa2e6b24c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Quiz table: scenario_type + roles
    op.add_column("quiz", sa.Column("scenario_type", sa.Text(), nullable=True))
    op.add_column("quiz", sa.Column("roles", sa.JSON(), nullable=True))

    # GameResults table: tabletop metadata
    op.add_column("game_results", sa.Column("player_roles", sa.JSON(), nullable=True))
    op.add_column("game_results", sa.Column("branch_path", sa.JSON(), nullable=True))
    op.add_column("game_results", sa.Column("facilitator_overrides", sa.JSON(), nullable=True))
    op.add_column("game_results", sa.Column("scenario_type", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("game_results", "scenario_type")
    op.drop_column("game_results", "facilitator_overrides")
    op.drop_column("game_results", "branch_path")
    op.drop_column("game_results", "player_roles")
    op.drop_column("quiz", "roles")
    op.drop_column("quiz", "scenario_type")
