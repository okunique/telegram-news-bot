"""update models

Revision ID: update_models
Revises: initial
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_models'
down_revision = 'initial'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем enum тип для market_type
    market_type = postgresql.ENUM('TRADFI', 'CRYPTO', name='market_type')
    market_type.create(op.get_bind())
    
    # Обновляем таблицу news
    op.alter_column('news', 'source_channel_id',
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('news', 'message_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('news', 'original_text',
                    existing_type=sa.Text(),
                    nullable=False)
    op.alter_column('news', 'translated_text',
                    existing_type=sa.Text(),
                    type_=sa.String())
    op.alter_column('news', 'market_target',
                    existing_type=sa.String(),
                    type_=sa.Enum('TRADFI', 'CRYPTO', name='market_type'))
    
    # Обновляем таблицу digest_logs
    op.alter_column('digest_logs', 'period',
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('digest_logs', 'news_count',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('digest_logs', 'topics_count',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    # Обновляем таблицу forecasts
    op.alter_column('forecasts', 'market_type',
                    existing_type=sa.String(),
                    type_=sa.Enum('TRADFI', 'CRYPTO', name='market_type'),
                    nullable=False)
    op.alter_column('forecasts', 'period',
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('forecasts', 'state',
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('forecasts', 'confidence',
                    existing_type=sa.String(),
                    type_=sa.Float(),
                    nullable=False)
    op.alter_column('forecasts', 'key_news',
                    existing_type=sa.Text(),
                    new_column_name='key_news_ids',
                    type_=sa.String())

def downgrade():
    # Откатываем изменения в таблице forecasts
    op.alter_column('forecasts', 'key_news_ids',
                    existing_type=sa.String(),
                    new_column_name='key_news',
                    type_=sa.Text())
    op.alter_column('forecasts', 'confidence',
                    existing_type=sa.Float(),
                    type_=sa.String(),
                    nullable=True)
    op.alter_column('forecasts', 'state',
                    existing_type=sa.String(),
                    nullable=True)
    op.alter_column('forecasts', 'period',
                    existing_type=sa.String(),
                    nullable=True)
    op.alter_column('forecasts', 'market_type',
                    existing_type=sa.Enum('TRADFI', 'CRYPTO', name='market_type'),
                    type_=sa.String())
    
    # Откатываем изменения в таблице digest_logs
    op.alter_column('digest_logs', 'topics_count',
                    existing_type=sa.Integer(),
                    nullable=True)
    op.alter_column('digest_logs', 'news_count',
                    existing_type=sa.Integer(),
                    nullable=True)
    op.alter_column('digest_logs', 'period',
                    existing_type=sa.String(),
                    nullable=True)
    
    # Откатываем изменения в таблице news
    op.alter_column('news', 'market_target',
                    existing_type=sa.Enum('TRADFI', 'CRYPTO', name='market_type'),
                    type_=sa.String())
    op.alter_column('news', 'translated_text',
                    existing_type=sa.String(),
                    type_=sa.Text())
    op.alter_column('news', 'original_text',
                    existing_type=sa.Text(),
                    nullable=True)
    op.alter_column('news', 'message_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    op.alter_column('news', 'source_channel_id',
                    existing_type=sa.String(),
                    nullable=True)
    
    # Удаляем enum тип
    market_type = postgresql.ENUM('TRADFI', 'CRYPTO', name='market_type')
    market_type.drop(op.get_bind()) 