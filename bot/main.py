import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from .config import settings
from .database import init_db
from .handlers import register_handlers
from .parser import start_parser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    try:
        # Инициализируем базу данных
        await init_db()
        logger.info("База данных инициализирована")
        
        # Создаем бота
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Создаем диспетчер
        dp = Dispatcher()
        
        # Регистрируем обработчики
        register_handlers(dp)
        logger.info("Обработчики зарегистрированы")
        
        # Запускаем парсер в отдельной задаче
        asyncio.create_task(start_parser())
        logger.info("Парсер запущен")
        
        # Запускаем бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 