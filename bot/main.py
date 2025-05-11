import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import structlog
from .config import settings
from .handlers import BotHandlers
from .models import Base

# Настройка логирования
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Создание движка базы данных
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    await init_db()
    
    # Создание сессии базы данных
    async with async_session() as session:
        # Создание обработчиков
        handlers = BotHandlers(session)
        
        # Создание приложения
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", handlers.start))
        application.add_handler(CommandHandler("status", handlers.status))
        application.add_handler(CommandHandler("digest", handlers.digest))
        application.add_handler(MessageHandler(filters.ALL, handlers.handle_message))
        
        # Запуск бота
        logger.info("Starting bot...")
        await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main()) 