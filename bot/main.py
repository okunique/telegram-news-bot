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
    try:
        # Инициализация базы данных
        await init_db()
        
        # Создание приложения
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Создание сессии базы данных
        async with async_session() as session:
            # Настройка обработчиков
            setup_handlers(application, session)
            
            # Запуск бота
            logger.info("Бот запущен")
            await application.initialize()
            await application.start()
            await application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise
    finally:
        if 'application' in locals():
            await application.stop()
            await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True) 