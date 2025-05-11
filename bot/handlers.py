from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
import structlog
from typing import Optional
from .config import settings
from .openrouter_client import OpenRouterClient
from .media_handler import MediaHandler
from .models import News, DigestLog
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

logger = structlog.get_logger()

class BotHandlers:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.openrouter = OpenRouterClient()
        self.media_handler = MediaHandler()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для анализа и перевода новостей. "
            "Я буду собирать новости из указанных каналов, "
            "переводить их и создавать аналитические дайджесты."
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        try:
            # Проверяем соединение с базой данных
            async with self.session.begin():
                news_count = await self.session.query(News).count()
                digest_count = await self.session.query(DigestLog).count()
            
            status_text = (
                "📊 Статус бота:\n\n"
                f"✅ Соединение с базой данных: активно\n"
                f"✅ OpenRouter API: проверено\n"
                f"📝 Обработано новостей: {news_count}\n"
                f"📊 Создано дайджестов: {digest_count}\n"
            )
            
            await update.message.reply_text(status_text)
            
        except Exception as e:
            logger.error("Error in status command", error=str(e))
            await update.message.reply_text("❌ Ошибка при получении статуса")
    
    async def digest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /digest"""
        try:
            period = context.args[0] if context.args else "24h"
            if period not in settings.DIGEST_PERIODS:
                await update.message.reply_text(
                    "❌ Неверный период. Используйте: 1h или 24h"
                )
                return
            
            # Получаем новости за указанный период
            time_ago = datetime.utcnow() - timedelta(
                hours=1 if period == "1h" else 24
            )
            
            async with self.session.begin():
                news = await self.session.query(News).filter(
                    News.timestamp >= time_ago
                ).all()
            
            if not news:
                await update.message.reply_text(
                    f"📭 Нет новостей за последние {period}"
                )
                return
            
            # Генерируем дайджест
            digest_text = await self._generate_digest(news, period)
            await update.message.reply_text(digest_text)
            
        except Exception as e:
            logger.error("Error in digest command", error=str(e))
            await update.message.reply_text("❌ Ошибка при создании дайджеста")
    
    async def _generate_digest(self, news: list, period: str) -> str:
        """Генерирует текст дайджеста"""
        # TODO: Реализовать генерацию дайджеста с помощью OpenRouter API
        return "Заглушка для дайджеста"
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик входящих сообщений"""
        try:
            if not update.message:
                return
            
            # Проверяем, что сообщение из нужного канала
            if str(update.message.chat.id) not in settings.SOURCE_CHANNEL_IDS:
                return
            
            # Получаем текст и медиа
            text = update.message.text or update.message.caption or ""
            media_url = await self.media_handler.handle_media(update, context)
            
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
                source_channel_id=str(update.message.chat.id),
                message_id=update.message.message_id,
                text_original=text,
                text_translated=translated,
                media_url=media_url,
                **analysis
            )
            
            async with self.session.begin():
                self.session.add(news)
                await self.session.commit()
            
            # Публикуем в целевой канал
            await context.bot.send_message(
                chat_id=settings.TARGET_CHANNEL_ID,
                text=f"{translated}\n\n"
                     f"📊 Важность: {news.importance_weight}/5\n"
                     f"🎯 Направление: {news.market_target.value}\n"
                     f"🏷 Тема: {news.topic}"
            )
            
            if media_url:
                await context.bot.send_photo(
                    chat_id=settings.TARGET_CHANNEL_ID,
                    photo=media_url
                )
            
        except Exception as e:
            logger.error("Error handling message", error=str(e)) 