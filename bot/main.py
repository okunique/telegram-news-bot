import logging
from telegram.ext import Application
from telegram import Update
from bot.config import settings
from bot.database import init_db, async_session
from bot.handlers import setup_handlers
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Инициализация базы данных
    asyncio.run(init_db())

    # Создание приложения
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Создание сессии базы данных
    async def run_bot():
        async with async_session() as session:
            setup_handlers(application, session)
            logger.info("Бот запущен")
            await application.run_polling()

    # Запуск бота
    asyncio.run(run_bot())

if __name__ == '__main__':
    main() 