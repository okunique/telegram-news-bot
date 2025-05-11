import logging
import structlog
from datetime import datetime, timedelta
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from .database import async_session
from .models import News, DigestLog
from .media_handler import MediaHandler
from .openrouter_client import OpenRouterClient

logger = structlog.get_logger()

class NewsHandler:
    def __init__(self, bot):
        self.bot = bot
        self.router = Router()
        self.media_handler = MediaHandler()
        self.openrouter = OpenRouterClient()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.router.message.register(self.handle_message, F.text)
        self.router.message.register(self.handle_media, F.photo)
        self.router.message.register(self.handle_media_group, F.media_group_id)
        self.router.message.register(self.digest, Command("digest"))
        self.router.message.register(self.status, Command("status"))
    
    async def handle_message(self, message: Message):
        """Обрабатывает текстовые сообщения"""
        try:
            async with async_session() as session:
                # Сохраняем новость
                news = News(
                    source_channel_id=message.chat.id,
                    message_id=message.message_id,
                    text=message.text,
                    timestamp=datetime.utcnow()
                )
                session.add(news)
                await session.commit()
                
                # Анализируем текст
                analysis = await self.openrouter.analyze_text(message.text)
                if analysis:
                    news.topic = analysis.get("topic")
                    news.confidence_level = analysis.get("confidence_level")
                    await session.commit()
                    
                    # Отправляем результат анализа
                    await message.reply(
                        f"📊 Анализ новости:\n"
                        f"Тема: {news.topic}\n"
                        f"Уверенность: {news.confidence_level}%"
                    )
                
        except Exception as e:
            logger.error("Error handling message", error=str(e))
            await message.reply("❌ Произошла ошибка при обработке сообщения")
    
    async def handle_media(self, message: Message):
        """Обрабатывает медиафайлы"""
        try:
            # Сохраняем медиафайл
            media_path = await self.media_handler.handle_media(message)
            if not media_path:
                return
            
            async with async_session() as session:
                # Сохраняем новость
                news = News(
                    source_channel_id=message.chat.id,
                    message_id=message.message_id,
                    text=message.caption or "",
                    media_path=media_path,
                    timestamp=datetime.utcnow()
                )
                session.add(news)
                await session.commit()
                
                # Анализируем текст
                if message.caption:
                    analysis = await self.openrouter.analyze_text(message.caption)
                    if analysis:
                        news.topic = analysis.get("topic")
                        news.confidence_level = analysis.get("confidence_level")
                        await session.commit()
                        
                        # Отправляем результат анализа
                        await message.reply(
                            f"📊 Анализ новости:\n"
                            f"Тема: {news.topic}\n"
                            f"Уверенность: {news.confidence_level}%"
                        )
                
        except Exception as e:
            logger.error("Error handling media", error=str(e))
            await message.reply("❌ Произошла ошибка при обработке медиафайла")
    
    async def handle_media_group(self, message: Message):
        """Обрабатывает группу медиафайлов"""
        try:
            # Получаем все сообщения из группы
            media_group = await self.bot.get_media_group(
                message.chat.id,
                message.message_id
            )
            
            # Сохраняем медиафайлы
            media_paths = await self.media_handler.handle_media_group(media_group)
            if not media_paths:
                return
            
            async with async_session() as session:
                # Сохраняем новость
                news = News(
                    source_channel_id=message.chat.id,
                    message_id=message.message_id,
                    text=message.caption or "",
                    media_path=",".join(media_paths),
                    timestamp=datetime.utcnow()
                )
                session.add(news)
                await session.commit()
                
                # Анализируем текст
                if message.caption:
                    analysis = await self.openrouter.analyze_text(message.caption)
                    if analysis:
                        news.topic = analysis.get("topic")
                        news.confidence_level = analysis.get("confidence_level")
                        await session.commit()
                        
                        # Отправляем результат анализа
                        await message.reply(
                            f"📊 Анализ новости:\n"
                            f"Тема: {news.topic}\n"
                            f"Уверенность: {news.confidence_level}%"
                        )
                
        except Exception as e:
            logger.error("Error handling media group", error=str(e))
            await message.reply("❌ Произошла ошибка при обработке группы медиафайлов")
    
    async def digest(self, message: Message):
        """Генерирует дайджест новостей"""
        try:
            # Получаем период из команды
            period = message.text.split()[1] if len(message.text.split()) > 1 else "day"
            if period not in ["hour", "day", "week"]:
                await message.reply("❌ Неверный период. Используйте: hour, day, week")
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
                    await message.reply("📭 Нет новостей за указанный период")
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
                await message.reply(digest_text)
                
        except Exception as e:
            logger.error("Error generating digest", error=str(e))
            await message.reply("❌ Произошла ошибка при генерации дайджеста")
    
    async def status(self, message: Message):
        """Показывает статус бота"""
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
                
                await message.reply(status_text)
                
        except Exception as e:
            logger.error("Error getting status", error=str(e))
            await message.reply("❌ Произошла ошибка при получении статуса") 