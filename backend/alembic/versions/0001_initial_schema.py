"""Initial schema: users, incidents, reports

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-31 10:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('google_sub', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('preferred_lang', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_users_google_sub', 'users', ['google_sub'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)

    # 2. incidents table
    # Column types with SQLite variant fallback
    reason_codes_col = sa.Column(
        'reason_codes',
        postgresql.ARRAY(sa.String()).with_variant(sa.JSON(), 'sqlite'),
        nullable=False
    )
    actions_shown_col = sa.Column(
        'actions_shown',
        postgresql.ARRAY(sa.String()).with_variant(sa.JSON(), 'sqlite'),
        nullable=False
    )

    op.create_table(
        'incidents',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('input_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        reason_codes_col,
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('domain_hash', sa.String(length=64), nullable=True),
        sa.Column('user_action_state', sa.String(length=50), nullable=True),
        actions_shown_col,
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('rules_version', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('idx_incidents_created_at', 'incidents', ['created_at'], unique=False)
    op.create_index('idx_incidents_category_risk', 'incidents', ['category', 'risk_level'], unique=False)
    op.create_index('idx_incidents_domain_hash', 'incidents', ['domain_hash'], unique=False)
    op.create_index('ix_incidents_user_id', 'incidents', ['user_id'], unique=False)

    # 3. reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', sa.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('verdict', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('idx_reports_created_at', 'reports', ['created_at'], unique=False)
    op.create_index('ix_reports_incident_id', 'reports', ['incident_id'], unique=False)
    op.create_index('ix_reports_user_id', 'reports', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('incidents')
    op.drop_table('users')

