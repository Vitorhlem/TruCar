"""Add is_reverted

Revision ID: a9883660547c
Revises: dd78b7132dcb
Create Date: 2025-11-17 09:33:24.959006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a9883660547c'
down_revision: Union[str, None] = 'dd78b7132dcb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('maintenance_part_changes', sa.Column('is_reverted', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_maintenance_part_changes_is_reverted'), 'maintenance_part_changes', ['is_reverted'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_maintenance_part_changes_is_reverted'), table_name='maintenance_part_changes')
    op.drop_column('maintenance_part_changes', 'is_reverted')
