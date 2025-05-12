import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select, func
from .database import async_session
from .models import News, Forecast
from .config import settings

logger = logging.getLogger(__name__)

class MarketForecast:
    def __init__(self):
        self.tradfi_topics = set(settings.TRADFI_TOPICS)
        self.crypto_topics = set(settings.CRYPTO_TOPICS)
    
    async def generate_forecast(self, period: str, market_type: str) -> Optional[Dict]:
        """
        Генерирует прогноз для указанного рынка и периода
        
        Args:
            period: 'hour' или 'day'
            market_type: 'TradFi' или 'Crypto'
        """
        try:
            # Определяем временной интервал
            now = datetime.utcnow()
            if period == "hour":
                time_ago = now - timedelta(hours=1)
            else:  # day
                time_ago = now - timedelta(days=1)
            
            async with async_session() as session:
                # Получаем новости за период
                stmt = select(News).where(
                    News.timestamp >= time_ago,
                    News.market_target.in_([market_type, "Both"])
                )
                result = await session.execute(stmt)
                news_list = result.scalars().all()
                
                if not news_list:
                    return None
                
                # Анализируем новости
                total_weight = 0
                weighted_sum = 0
                key_news = []
                
                for news in news_list:
                    weight = news.importance
                    total_weight += weight
                    
                    # Определяем направление влияния
                    if news.topic in self.tradfi_topics:
                        direction = 1 if "positive" in news.original_text.lower() else -1
                    else:
                        direction = 1 if "bullish" in news.original_text.lower() else -1
                    
                    weighted_sum += weight * direction
                    
                    # Добавляем важные новости
                    if news.importance >= 4 or news.is_catalyst:
                        key_news.append({
                            "text": news.translated_text,
                            "importance": news.importance,
                            "is_catalyst": news.is_catalyst
                        })
                
                # Определяем состояние рынка
                if total_weight == 0:
                    return None
                
                sentiment = weighted_sum / total_weight
                
                if sentiment > 0.3:
                    state = "bullish"
                elif sentiment < -0.3:
                    state = "bearish"
                else:
                    state = "neutral"
                
                # Определяем уверенность
                if len(key_news) >= 3:
                    confidence = "high"
                elif len(key_news) >= 1:
                    confidence = "medium"
                else:
                    confidence = "low"
                
                # Сохраняем прогноз
                forecast = Forecast(
                    market_type=market_type,
                    period=period,
                    state=state,
                    confidence=confidence,
                    key_news=str(key_news),
                    generated_at=now
                )
                session.add(forecast)
                await session.commit()
                
                return {
                    "market_type": market_type,
                    "period": period,
                    "state": state,
                    "confidence": confidence,
                    "key_news": key_news
                }
                
        except Exception as e:
            logger.error(f"Ошибка при генерации прогноза: {e}")
            return None
    
    async def get_latest_forecast(self, market_type: str) -> Optional[Dict]:
        """Получает последний прогноз для указанного рынка"""
        try:
            async with async_session() as session:
                stmt = select(Forecast).where(
                    Forecast.market_type == market_type
                ).order_by(Forecast.generated_at.desc()).limit(1)
                
                result = await session.execute(stmt)
                forecast = result.scalar_one_or_none()
                
                if forecast:
                    return {
                        "market_type": forecast.market_type,
                        "period": forecast.period,
                        "state": forecast.state,
                        "confidence": forecast.confidence,
                        "key_news": eval(forecast.key_news),
                        "generated_at": forecast.generated_at
                    }
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при получении прогноза: {e}")
            return None 