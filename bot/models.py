from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base

class News(Base):
    """Модель новости"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    source_channel_id = Column(String, nullable=False)
    message_id = Column(Integer, nullable=False)
    original_text = Column(String, nullable=False)
    translated_text = Column(String)
    topic = Column(String)
    confidence = Column(Float)
    importance = Column(Integer)  # 1-5
    is_catalyst = Column(Boolean, default=False)
    market_target = Column(Enum("TRADFI", "CRYPTO", name="market_type"))
    media_path = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<News(id={self.id}, topic={self.topic}, importance={self.importance})>"

class DigestLog(Base):
    """Модель лога дайджеста"""
    __tablename__ = "digest_logs"
    
    id = Column(Integer, primary_key=True)
    period = Column(String, nullable=False)  # hour, day, week
    news_count = Column(Integer, nullable=False)
    topics_count = Column(Integer, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DigestLog(id={self.id}, period={self.period}, news_count={self.news_count})>"

class Forecast(Base):
    """Модель прогноза рынка"""
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True)
    market_type = Column(Enum("TRADFI", "CRYPTO", name="market_type"), nullable=False)
    period = Column(String, nullable=False)  # hour, day, week
    state = Column(String, nullable=False)  # bullish, bearish, neutral
    confidence = Column(Float, nullable=False)
    key_news_ids = Column(String)  # JSON array of news IDs
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Forecast(id={self.id}, market_type={self.market_type}, state={self.state})>" 