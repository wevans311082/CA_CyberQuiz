# SPDX-FileCopyrightText: 2026
#
# SPDX-License-Identifier: MPL-2.0

"""Added tabletop score persistence fields to game_results

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("game_results", sa.Column("company_score", sa.Float(), nullable=True))
    op.add_column("game_results", sa.Column("company_score_timeline", sa.JSON(), nullable=True))
    op.add_column("game_results", sa.Column("score_visibility_policy", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("game_results", "score_visibility_policy")
    op.drop_column("game_results", "company_score_timeline")
    op.drop_column("game_results", "company_score")
