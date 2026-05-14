"""add document_id to conversations

Revision ID: e3f4a5b6c7d8
Revises: a1b2c3d4e5f6
Create Date: 2026-05-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'conversations',
        sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('conversations', 'document_id')
