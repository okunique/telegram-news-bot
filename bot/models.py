from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class MarketTarget(str, Enum):
    TRADFI = "TradFi"
    CRYPTO = "Crypto"
    BOTH = "Both"

class News(Base):
    __tablename__ = "news"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_channel_id = Column(String, nullable=False)
    message_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    text_original = Column(String, nullable=False)
    text_translated = Column(String, nullable=False)
    media_url = Column(String, nullable=True)
    topic = Column(String, nullable=False)
    market_target = Column(SQLEnum(MarketTarget), nullable=False)
    importance_weight = Column(Integer, nullable=False)
    is_catalyst = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<News(id={self.id}, topic={self.topic}, weight={self.importance_weight})>"

class DigestLog(Base):
    __tablename__ = "digest_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generated_at = Column(DateTime, default=datetime.utcnow)
    period = Column(String, nullable=False)  # "1h" or "24h"
    content_text = Column(String, nullable=False)
    confidence_level = Column(String, nullable=False)  # "low", "medium", "high"
    
    def __repr__(self):
        return f"<DigestLog(id={self.id}, period={self.period}, confidence={self.confidence_level})>" 