import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения"""
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # База данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/newsbot"
    )
    
    # OpenRouter API
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Каналы
    SOURCE_CHANNEL_IDS: str = os.getenv("SOURCE_CHANNEL_IDS", "[]")
    TARGET_CHANNEL_ID: str = os.getenv("TARGET_CHANNEL_ID", "")
    
    # PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "newsbot")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    # Режим отладки
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

# Создаем экземпляр настроек
settings = Settings() 