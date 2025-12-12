"""add token_usage table

Revision ID: e1f2a3b4c5d6
Revises: 018012973d35
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = '018012973d35'  # Latest migration: add_indexes
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'token_usage',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_user_created', 'token_usage', ['user_id', 'created_at'])
    op.create_index(op.f('ix_token_usage_user_id'), 'token_usage', ['user_id'], unique=False)
    op.create_index(op.f('ix_token_usage_created_at'), 'token_usage', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_token_usage_created_at'), table_name='token_usage')
    op.drop_index(op.f('ix_token_usage_user_id'), table_name='token_usage')
    op.drop_index('idx_user_created', table_name='token_usage')
    op.drop_table('token_usage')

