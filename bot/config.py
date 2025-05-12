from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения"""
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    
    # Telegram User API
    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str
    
    # Каналы
    SOURCE_CHANNEL_IDS: str
    TARGET_CHANNEL_ID: str = "-1001556054753"  # ID канала для публикации новостей
    
    # База данных
    DATABASE_URL: str
    
    # Топики для анализа
    TRADFI_TOPICS: List[str] = [
        "экономика",
        "геополитика",
        "энергетика",
        "политика",
        "финансы",
        "акции",
        "облигации",
        "форекс"
    ]
    CRYPTO_TOPICS: List[str] = [
        "криптовалюты",
        "DeFi",
        "Web3",
        "NFT",
        "блокчейн",
        "токены",
        "смарт-контракты"
    ]
    
    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "anthropic/claude-3-opus-20240229"
    
    # Настройки приложения
    DEBUG: bool = False
    
    @property
    def source_channels(self) -> List[str]:
        """Получить список ID каналов-источников"""
        return [ch.strip() for ch in self.SOURCE_CHANNEL_IDS.split(',')]
    
    @property
    def api_id(self) -> int:
        """Получить API ID как целое число"""
        return int(self.TELEGRAM_API_ID)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Создаем экземпляр настроек
settings = Settings() 