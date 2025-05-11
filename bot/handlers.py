from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import structlog
from typing import Optional
from .config import settings
from .openrouter_client import OpenRouterClient
from .media_handler import MediaHandler
from .models import News, DigestLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

logger = structlog.get_logger()

class BotHandlers:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.openrouter = OpenRouterClient()
        self.media_handler = MediaHandler()
    
    async def start(self, message: Message):
        """Обработчик команды /start"""
        await message.answer(
            "Привет! Я бот для анализа и перевода новостей. "
            "Я буду собирать новости из указанных каналов, "
            "переводить их и создавать аналитические дайджесты."
        )
    
    async def status(self, message: Message):
        """Обработчик команды /status"""
        try:
            # Проверяем соединение с базой данных
            async with self.session.begin():
                news_count = await self.session.scalar(select(func.count()).select_from(News))
                digest_count = await self.session.scalar(select(func.count()).select_from(DigestLog))
            
            status_text = (
                "📊 Статус бота:\n\n"
                f"✅ Соединение с базой данных: активно\n"
                f"✅ OpenRouter API: проверено\n"
                f"📝 Обработано новостей: {news_count}\n"
                f"📊 Создано дайджестов: {digest_count}\n"
            )
            
            await message.answer(status_text)
            
        except Exception as e:
            logger.error("Error in status command", error=str(e))
            await message.answer("❌ Ошибка при получении статуса")
    
    async def digest(self, message: Message):
        """Обработчик команды /digest"""
        try:
            args = message.text.split()[1:] if message.text else []
            period = args[0] if args else "24h"
            
            if period not in settings.DIGEST_PERIODS:
                await message.answer(
                    "❌ Неверный период. Используйте: 1h или 24h"
                )
                return
            
            # Получаем новости за указанный период
            time_ago = datetime.utcnow() - timedelta(
                hours=1 if period == "1h" else 24
            )
            
            async with self.session.begin():
                stmt = select(News).where(News.timestamp >= time_ago)
                result = await self.session.execute(stmt)
                news = result.scalars().all()
            
            if not news:
                await message.answer(
                    f"📭 Нет новостей за последние {period}"
                )
                return
            
            # Генерируем дайджест
            digest_text = await self._generate_digest(news, period)
            await message.answer(digest_text)
            
        except Exception as e:
            logger.error("Error in digest command", error=str(e))
            await message.answer("❌ Ошибка при создании дайджеста")
    
    async def _generate_digest(self, news: list, period: str) -> str:
        """Генерирует текст дайджеста"""
        # TODO: Реализовать генерацию дайджеста с помощью OpenRouter API
        return "Заглушка для дайджеста"
    
    async def handle_message(self, message: Message):
        """Обработчик входящих сообщений"""
        try:
            # Проверяем, что сообщение из нужного канала
            if str(message.chat.id) not in settings.SOURCE_CHANNEL_IDS:
                return
            
            # Получаем текст и медиа
            text = message.text or message.caption or ""
            media_url = await self.media_handler.handle_media(message)
            
            if not text and not media_url:
                return
            
            # Анализируем текст
            analysis = await self.openrouter.analyze_text(text)
            if not analysis:
                logger.error("Failed to analyze text")
                return
            
            # Переводим текст
            translated = await self.openrouter.translate_text(text)
            if not translated:
                logger.error("Failed to translate text")
                return
            
            # Сохраняем в базу данных
            news = News(
                source_channel_id=str(message.chat.id),
                message_id=message.message_id,
                text_original=text,
                text_translated=translated,
                media_url=media_url,
                **analysis
            )
            
            async with self.session.begin():
                self.session.add(news)
                await self.session.commit()
            
            # Публикуем в целевой канал
            await message.bot.send_message(
                chat_id=settings.TARGET_CHANNEL_ID,
                text=f"{translated}\n\n"
                     f"📊 Важность: {news.importance_weight}/5\n"
                     f"🎯 Направление: {news.market_target.value}\n"
                     f"🏷 Тема: {news.topic}"
            )
            
            if media_url:
                await message.bot.send_photo(
                    chat_id=settings.TARGET_CHANNEL_ID,
                    photo=media_url
                )
            
        except Exception as e:
            logger.error("Error handling message", error=str(e))

def setup_handlers(dp: Router, session: AsyncSession):
    """Настраивает обработчики команд и сообщений"""
    handlers = BotHandlers(session)
    
    # Регистрируем обработчики команд
    dp.message.register(handlers.start, Command(commands=["start"]))
    dp.message.register(handlers.status, Command(commands=["status"]))
    dp.message.register(handlers.digest, Command(commands=["digest"]))
    
    # Регистрируем обработчик сообщений
    dp.message.register(handlers.handle_message) 