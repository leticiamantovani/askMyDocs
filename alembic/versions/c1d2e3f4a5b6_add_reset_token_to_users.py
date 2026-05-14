"""add reset token to users

Revision ID: c1d2e3f4a5b6
Revises: bfa90355c6b3
Create Date: 2026-05-13

"""
from alembic import op
import sqlalchemy as sa

revision = "c1d2e3f4a5b6"
down_revision = "bfa90355c6b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("reset_token", sa.String(), nullable=True))
    op.add_column("users", sa.Column("reset_token_expires", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "reset_token_expires")
    op.drop_column("users", "reset_token")
