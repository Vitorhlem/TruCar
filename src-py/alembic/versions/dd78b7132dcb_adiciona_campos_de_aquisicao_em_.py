"""Adiciona campos de aquisicao em implements

Revision ID: dd78b7132dcb
Revises: 
Create Date: 2025-11-14 23:34:07.255315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'dd78b7132dcb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('implements', sa.Column('acquisition_date', sa.Date(), nullable=True))
    op.add_column('implements', sa.Column('acquisition_value', sa.Float(), nullable=True))
    op.add_column('implements', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('implements', 'notes')
    op.drop_column('implements', 'acquisition_value')
    op.drop_column('implements', 'acquisition_date')
