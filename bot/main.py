import asyncio
import logging
import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from .config import settings
from .handlers import NewsHandler
from .database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

async def main():
    # Инициализация базы данных
    await init_db()
    
    # Инициализация бота
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация хендлеров
    news_handler = NewsHandler(bot)
    dp.include_router(news_handler.router)
    
    # Запуск бота
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 