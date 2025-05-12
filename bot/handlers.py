import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from .database import async_session
from .models import News, DigestLog, Forecast
from .openrouter_client import analyze_news_full, translate_news
from .forecast import MarketForecast
from .config import settings

logger = logging.getLogger(__name__)

def register_handlers(dp: Router):
    """Настройка обработчиков команд"""
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_status, Command(commands=["status"]))
    dp.message.register(cmd_digest, Command(commands=["digest"]))
    dp.message.register(cmd_forecast, Command(commands=["forecast"]))
    dp.message.register(handle_message, F.text)
    dp.message.register(handle_photo, F.photo)

async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для анализа новостей.\n\n"
        "Доступные команды:\n"
        "/help - показать справку\n"
        "/status - показать статус бота\n"
        "/digest [период] - получить дайджест новостей\n"
        "/forecast [рынок] - получить прогноз рынка"
    )

async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📚 Справка по командам:\n\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/status - показать статистику бота\n"
        "/digest [период] - получить дайджест новостей\n"
        "  Периоды: hour, day, week\n"
        "  Пример: /digest day\n"
        "/forecast [рынок] - получить прогноз рынка\n"
        "  Рынки: tradfi, crypto\n"
        "  Пример: /forecast tradfi"
    )

async def cmd_status(message: Message):
    """Обработчик команды /status"""
    try:
        async with async_session() as session:
            # Получаем статистику
            total_news = await session.execute(select(func.count(News.id)))
            total_news = total_news.scalar()
            
            total_digests = await session.execute(select(func.count(DigestLog.id)))
            total_digests = total_digests.scalar()
            
            total_forecasts = await session.execute(select(func.count(Forecast.id)))
            total_forecasts = total_forecasts.scalar()
            
            # Формируем сообщение
            status_text = (
                "🤖 Статус бота:\n\n"
                f"📊 Всего новостей: {total_news}\n"
                f"📈 Сгенерировано дайджестов: {total_digests}\n"
                f"📊 Сгенерировано прогнозов: {total_forecasts}\n"
                f"⏰ Время сервера: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
            
            await message.answer(status_text)
            
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        await message.answer("❌ Произошла ошибка при получении статуса")

async def cmd_digest(message: Message):
    """Обработчик команды /digest"""
    try:
        # Получаем период из команды
        args = message.text.split()
        period = args[1] if len(args) > 1 else "day"
        
        if period not in ["hour", "day", "week"]:
            await message.answer(
                "❌ Неверный период. Используйте: hour, day, week"
            )
            return
        
        # Вычисляем время начала периода
        now = datetime.utcnow()
        if period == "hour":
            time_ago = now - timedelta(hours=1)
        elif period == "day":
            time_ago = now - timedelta(days=1)
        else:  # week
            time_ago = now - timedelta(weeks=1)
        
        async with async_session() as session:
            # Получаем новости за период
            stmt = select(News).where(News.timestamp >= time_ago)
            result = await session.execute(stmt)
            news_list = result.scalars().all()
            
            if not news_list:
                await message.answer("📭 Нет новостей за указанный период")
                return
            
            # Группируем новости по темам
            topics = {}
            for news in news_list:
                if news.topic:
                    if news.topic not in topics:
                        topics[news.topic] = []
                    topics[news.topic].append(news)
            
            # Формируем дайджест
            digest_text = f"📰 Дайджест новостей за {period}:\n\n"
            for topic, news in topics.items():
                digest_text += f"📌 {topic}:\n"
                for n in news:
                    digest_text += f"- {n.translated_text[:100]}...\n"
                    if n.importance >= 4:
                        digest_text += "  ⚠️ Важная новость!\n"
                    if n.is_catalyst:
                        digest_text += "  🔥 Катализатор рынка!\n"
                digest_text += "\n"
            
            # Сохраняем лог дайджеста
            log = DigestLog(
                period=period,
                news_count=len(news_list),
                topics_count=len(topics),
                generated_at=now
            )
            session.add(log)
            await session.commit()
            
            # Отправляем дайджест
            await message.answer(digest_text)
            
    except Exception as e:
        logger.error(f"Ошибка при генерации дайджеста: {e}")
        await message.answer("❌ Произошла ошибка при генерации дайджеста")

async def cmd_forecast(message: Message):
    """Обработчик команды /forecast"""
    try:
        # Получаем тип рынка из команды
        args = message.text.split()
        market_type = args[1].upper() if len(args) > 1 else "TRADFI"
        
        if market_type not in ["TRADFI", "CRYPTO"]:
            await message.answer(
                "❌ Неверный тип рынка. Используйте: tradfi, crypto"
            )
            return
        
        # Генерируем прогноз
        forecast = MarketForecast()
        result = await forecast.generate_forecast("day", market_type)
        
        if not result:
            await message.answer("📭 Недостаточно данных для прогноза")
            return
        
        # Формируем сообщение
        forecast_text = (
            f"📊 Прогноз {market_type}:\n\n"
            f"Состояние: {result['state']}\n"
            f"Уверенность: {result['confidence']}\n\n"
            "Ключевые новости:\n"
        )
        
        for news in result["key_news"]:
            forecast_text += f"- {news['text'][:100]}...\n"
            if news["is_catalyst"]:
                forecast_text += "  🔥 Катализатор!\n"
        
        await message.answer(forecast_text)
        
    except Exception as e:
        logger.error(f"Ошибка при генерации прогноза: {e}")
        await message.answer("❌ Произошла ошибка при генерации прогноза")

async def handle_message(message: Message):
    """Обработчик текстовых сообщений"""
    try:
        # Проверяем, что сообщение из нужного канала
        if str(message.chat.id) not in settings.SOURCE_CHANNEL_IDS:
            return
        
        # Анализируем новость
        analysis = await analyze_news_full(message.text)
        if not analysis:
            logger.error("Не удалось проанализировать новость")
            return
        
        # Переводим новость
        translated = await translate_news(message.text)
        if not translated:
            logger.error("Не удалось перевести новость")
            return
        
        async with async_session() as session:
            # Сохраняем новость
            news = News(
                source_channel_id=message.chat.id,
                message_id=message.message_id,
                original_text=message.text,
                translated_text=translated,
                topic=analysis["topic"],
                confidence=analysis["confidence"],
                importance=analysis["importance"],
                is_catalyst=analysis["is_catalyst"],
                market_target=analysis["market_target"],
                timestamp=datetime.utcnow()
            )
            session.add(news)
            await session.commit()
            
            # Публикуем в целевой канал
            if translated:
                await message.bot.send_message(
                    chat_id=settings.TARGET_CHANNEL_ID,
                    text=f"📰 {translated}\n\n"
                         f"Тема: {analysis['topic']}\n"
                         f"Важность: {analysis['importance']}/5\n"
                         f"Катализатор: {'Да' if analysis['is_catalyst'] else 'Нет'}"
                )
            
            # Если новость важная или катализатор, обновляем прогноз
            if analysis["importance"] >= 4 or analysis["is_catalyst"]:
                forecast = MarketForecast()
                await forecast.generate_forecast("day", analysis["market_target"])
            
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

async def handle_photo(message: Message):
    """Обработчик фотографий"""
    try:
        # Проверяем, что сообщение из нужного канала
        if str(message.chat.id) not in settings.SOURCE_CHANNEL_IDS:
            return
        
        caption = message.caption or ""
        if not caption:
            return
        
        # Анализируем новость
        analysis = await analyze_news_full(caption)
        if not analysis:
            logger.error("Не удалось проанализировать новость")
            return
        
        # Переводим новость
        translated = await translate_news(caption)
        if not translated:
            logger.error("Не удалось перевести новость")
            return
        
        async with async_session() as session:
            # Сохраняем новость
            news = News(
                source_channel_id=message.chat.id,
                message_id=message.message_id,
                original_text=caption,
                translated_text=translated,
                topic=analysis["topic"],
                confidence=analysis["confidence"],
                importance=analysis["importance"],
                is_catalyst=analysis["is_catalyst"],
                market_target=analysis["market_target"],
                media_path=message.photo[-1].file_id,
                timestamp=datetime.utcnow()
            )
            session.add(news)
            await session.commit()
            
            # Публикуем в целевой канал
            if translated:
                await message.bot.send_photo(
                    chat_id=settings.TARGET_CHANNEL_ID,
                    photo=message.photo[-1].file_id,
                    caption=f"📰 {translated}\n\n"
                            f"Тема: {analysis['topic']}\n"
                            f"Важность: {analysis['importance']}/5\n"
                            f"Катализатор: {'Да' if analysis['is_catalyst'] else 'Нет'}"
                )
            
            # Если новость важная или катализатор, обновляем прогноз
            if analysis["importance"] >= 4 or analysis["is_catalyst"]:
                forecast = MarketForecast()
                await forecast.generate_forecast("day", analysis["market_target"])
            
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}") 