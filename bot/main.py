import asyncio
import logging
from telegram.ext import Application
from telegram import Update
from bot.config import settings
from bot.database import init_db, async_session
from bot.handlers import setup_handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    # Инициализация базы данных
    await init_db()

    # Создание приложения
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Создание сессии базы данных
    # Для простоты: создаём новую сессию на каждый апдейт через partial
    from functools import partial
    from sqlalchemy.ext.asyncio import AsyncSession
    async def session_factory():
        async with async_session() as session:
            yield session
    setup_handlers(application, partial(session_factory))

    logger.info("Бот запущен")
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main()) 