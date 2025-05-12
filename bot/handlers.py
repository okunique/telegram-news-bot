import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from .database import async_session
from .models import News, DigestLog
from .openrouter_client import analyze_news

logger = logging.getLogger(__name__)

def register_handlers(dp: Router):
    """Настройка обработчиков команд"""
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_status, Command(commands=["status"]))
    dp.message.register(cmd_digest, Command(commands=["digest"]))
    dp.message.register(handle_message, F.text)
    dp.message.register(handle_photo, F.photo)

async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для анализа новостей.\n\n"
        "Доступные команды:\n"
        "/help - показать справку\n"
        "/status - показать статус бота\n"
        "/digest - получить дайджест новостей"
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
        "  Пример: /digest day"
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
            
            # Формируем сообщение
            status_text = (
                "🤖 Статус бота:\n\n"
                f"📊 Всего новостей: {total_news}\n"
                f"📈 Сгенерировано дайджестов: {total_digests}\n"
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
                    digest_text += f"- {n.text[:100]}...\n"
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

async def handle_message(message: Message):
    """Обработчик текстовых сообщений с анализом"""
    try:
        # Анализируем новость
        topic, confidence = await analyze_news(message.text)
        async with async_session() as session:
            news = News(
                source_channel_id=message.chat.id,
                message_id=message.message_id,
                text=message.text,
                topic=topic,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            session.add(news)
            await session.commit()
        await message.reply(f"✅ Новость сохранена\nТема: {topic}\nУверенность: {confidence}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await message.reply("❌ Произошла ошибка при обработке сообщения")

async def handle_photo(message: Message):
    """Обработчик фотографий с анализом caption"""
    try:
        caption = message.caption or ""
        topic, confidence = await analyze_news(caption) if caption else (None, None)
        async with async_session() as session:
            news = News(
                source_channel_id=message.chat.id,
                message_id=message.message_id,
                text=caption,
                topic=topic,
                confidence=confidence,
                media_path=message.photo[-1].file_id,  # Используем file_id как путь
                timestamp=datetime.utcnow()
            )
            session.add(news)
            await session.commit()
        await message.reply(f"✅ Фото сохранено\nТема: {topic}\nУверенность: {confidence}")
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        await message.reply("❌ Произошла ошибка при обработке фото") 