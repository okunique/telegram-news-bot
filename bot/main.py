import logging
from telegram.ext import Application
from telegram import Update
from bot.config import settings
from bot.database import init_db, async_session
from bot.handlers import setup_handlers
import asyncio
import nest_asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Разрешаем вложенные event loops
nest_asyncio.apply()

async def main():
    # Инициализация базы данных
    await init_db()

    # Создание приложения
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Создание сессии базы данных
    async with async_session() as session:
        setup_handlers(application, session)
        logger.info("Бот запущен")
        await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main()) 