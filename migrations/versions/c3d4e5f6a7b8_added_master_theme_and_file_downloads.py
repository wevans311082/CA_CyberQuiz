# SPDX-FileCopyrightText: 2026
#
# SPDX-License-Identifier: MPL-2.0

"""Added master_theme to quiz and file_downloads_log to game_results

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Quiz table: master_theme JSON blob
    op.add_column("quiz", sa.Column("master_theme", sa.JSON(), nullable=True))

    # GameResults table: file download audit log
    op.add_column("game_results", sa.Column("file_downloads_log", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("game_results", "file_downloads_log")
    op.drop_column("quiz", "master_theme")
