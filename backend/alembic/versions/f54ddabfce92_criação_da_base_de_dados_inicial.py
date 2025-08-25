"""Cria base de dados completa e final

Revision ID: 0001
Revises: 
Create Date: 2025-08-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### CRIAÇÃO DE TODAS AS TABELAS NA ORDEM CORRETA DE DEPENDÊNCIA ###
    
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sector', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    op.create_table('vehicles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('license_plate', sa.String(length=20), nullable=True),
        sa.Column('identifier', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('photo_url', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_km', sa.Integer(), nullable=False, default=0),
        sa.Column('current_engine_hours', sa.Float(), nullable=True, default=0),
        sa.Column('next_maintenance_date', sa.Date(), nullable=True),
        sa.Column('next_maintenance_km', sa.Integer(), nullable=True),
        sa.Column('maintenance_notes', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('license_plate')
    )
    
    op.create_table('journeys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('start_mileage', sa.Integer(), nullable=False),
        sa.Column('end_mileage', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('trip_type', sa.String(length=50), nullable=False),
        sa.Column('destination_address', sa.String(), nullable=True),
        sa.Column('trip_description', sa.String(), nullable=True),
        sa.Column('start_engine_hours', sa.Float(), nullable=True),
        sa.Column('end_engine_hours', sa.Float(), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('fuel_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('odometer', sa.Integer(), nullable=False),
        sa.Column('liters', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('receipt_photo_url', sa.String(length=512), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('maintenance_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('problem_description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('manager_notes', sa.Text(), nullable=True),
        sa.Column('reported_by_id', sa.Integer(), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['reported_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('maintenance_comments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('file_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['maintenance_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('related_vehicle_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['related_vehicle_id'], ['vehicles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('location_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # ### Ordem inversa para apagar ###
    op.drop_table('location_history')
    op.drop_table('notifications')
    op.drop_table('maintenance_comments')
    op.drop_table('maintenance_requests')
    op.drop_table('fuel_logs')
    op.drop_table('journeys')
    op.drop_table('vehicles')
    op.drop_table('users')
    op.drop_table('organizations')