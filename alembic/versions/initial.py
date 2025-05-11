"""initial

Revision ID: initial
Revises: 
Create Date: 2024-05-11 23:59:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу news
    op.create_table(
        'news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_channel_id', sa.String(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=True),
        sa.Column('media_path', sa.String(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Создаем таблицу digest_logs
    op.create_table(
        'digest_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(), nullable=False),
        sa.Column('news_count', sa.Integer(), nullable=False),
        sa.Column('topics_count', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('digest_logs')
    op.drop_table('news') 