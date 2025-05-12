from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения"""
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    SOURCE_CHANNEL_IDS: str  # Будет преобразовано в список
    
    # База данных
    DATABASE_URL: str
    
    # Топики для анализа
    TRADFI_TOPICS: List[str] = [
        "экономика", "ФРС", "инфляция", "ставки", "рынок", 
        "акции", "облигации", "недвижимость", "трейдинг"
    ]
    CRYPTO_TOPICS: List[str] = [
        "биткоин", "альткоины", "DeFi", "NFT", "блокчейн",
        "майнинг", "токены", "смарт-контракты"
    ]
    
    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "anthropic/claude-3-opus-20240229"
    
    # Настройки приложения
    DEBUG: bool = False
    
    @property
    def source_channels(self) -> List[str]:
        """Получить список ID каналов-источников"""
        return [ch.strip() for ch in self.SOURCE_CHANNEL_IDS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Создаем экземпляр настроек
settings = Settings() 