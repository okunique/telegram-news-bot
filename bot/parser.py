import logging
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, MessageMediaPhoto, MessageMediaDocument
from .config import settings
from .database import async_session
from .models import News
from .openrouter_client import analyze_news_full, translate_news

logger = logging.getLogger(__name__)

class NewsParser:
    def __init__(self):
        self.client = TelegramClient(
            "news_parser_session",
            settings.api_id,
            settings.TELEGRAM_API_HASH
        )
        self.source_channels = settings.SOURCE_CHANNEL_IDS
        self.target_channel = settings.TARGET_CHANNEL_ID
        self.last_check = datetime.utcnow() - timedelta(hours=1)
    
    async def start(self):
        """Запуск парсера"""
        try:
            await self.client.start()
            logger.info("Парсер запущен")
            
            # Регистрируем обработчик новых сообщений
            @self.client.on(events.NewMessage(chats=self.source_channels))
            async def handle_new_message(event):
                await self.process_message(event.message)
            
            # Запускаем клиент
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Ошибка при запуске парсера: {e}")
            raise
    
    async def process_message(self, message):
        """Обработка нового сообщения"""
        try:
            # Проверяем, что сообщение не старше последней проверки
            if message.date < self.last_check:
                return
            
            # Получаем текст сообщения
            text = message.text or message.caption or ""
            if not text:
                return
            
            # Анализируем новость
            analysis = await analyze_news_full(text)
            if not analysis:
                logger.error("Не удалось проанализировать новость")
                return
            
            # Переводим новость
            translated = await translate_news(text)
            if not translated:
                logger.error("Не удалось перевести новость")
                return
            
            # Сохраняем новость в базу
            async with async_session() as session:
                news = News(
                    source_channel_id=str(message.chat_id),
                    message_id=message.id,
                    original_text=text,
                    translated_text=translated,
                    topic=analysis["topic"],
                    confidence=analysis["confidence"],
                    importance=analysis["importance"],
                    is_catalyst=analysis["is_catalyst"],
                    market_target=analysis["market_target"],
                    timestamp=message.date
                )
                
                # Если есть медиа, сохраняем его
                if message.media:
                    if isinstance(message.media, MessageMediaPhoto):
                        news.media_path = "photo"
                    elif isinstance(message.media, MessageMediaDocument):
                        news.media_path = "document"
                
                session.add(news)
                await session.commit()
                
                # Публикуем в целевой канал
                if translated:
                    # Отправляем текст
                    await self.client.send_message(
                        self.target_channel,
                        f"📰 {translated}\n\n"
                        f"Тема: {analysis['topic']}\n"
                        f"Важность: {analysis['importance']}/5\n"
                        f"Катализатор: {'Да' if analysis['is_catalyst'] else 'Нет'}"
                    )
                    
                    # Если есть медиа, отправляем его
                    if message.media:
                        await self.client.send_file(
                            self.target_channel,
                            message.media,
                            caption=f"📰 {translated}"
                        )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
    
    async def fetch_history(self, hours: int = 1):
        """Получение истории сообщений за последние N часов"""
        try:
            time_ago = datetime.utcnow() - timedelta(hours=hours)
            
            for channel in self.source_channels:
                async for message in self.client.iter_messages(
                    channel,
                    offset_date=time_ago,
                    reverse=True
                ):
                    await self.process_message(message)
            
            self.last_check = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Ошибка при получении истории: {e}")
    
    async def stop(self):
        """Остановка парсера"""
        try:
            await self.client.disconnect()
            logger.info("Парсер остановлен")
        except Exception as e:
            logger.error(f"Ошибка при остановке парсера: {e}")

# Создаем экземпляр парсера
parser = NewsParser()

async def start_parser():
    """Запуск парсера"""
    try:
        # Получаем историю за последний час
        await parser.fetch_history(hours=1)
        
        # Запускаем парсер
        await parser.start()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске парсера: {e}")
        raise 