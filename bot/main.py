import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
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

    # Создание бота и диспетчера
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Создание сессии базы данных
    async with async_session() as session:
        # Настройка обработчиков
        setup_handlers(dp, session)
        
        logger.info("Бот запущен")
        # Запуск бота
        await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 