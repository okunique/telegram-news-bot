from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class News(Base):
    """Модель новости"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    source_channel_id = Column(String, nullable=False)
    message_id = Column(Integer, nullable=False)
    text = Column(String)
    media_path = Column(String)
    topic = Column(String)
    confidence_level = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<News(id={self.id}, topic={self.topic})>"

class DigestLog(Base):
    """Модель лога дайджеста"""
    __tablename__ = "digest_logs"
    
    id = Column(Integer, primary_key=True)
    period = Column(String, nullable=False)
    news_count = Column(Integer, nullable=False)
    topics_count = Column(Integer, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DigestLog(id={self.id}, period={self.period})>" 