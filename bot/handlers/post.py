from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session
from ..models import News
from ..config import settings
from ..openrouter_client import analyze_news

router = Router()

@router.message(F.text)
async def handle_text(message: Message):
    """Обработка текстовых сообщений"""
    if str(message.chat.id) not in settings.SOURCE_CHANNEL_IDS:
        return
    
    # Сохраняем новость
    async with async_session() as session:
        news = News(
            source_channel_id=str(message.chat.id),
            message_id=message.message_id,
            text=message.text
        )
        session.add(news)
        await session.commit()
        
        # Анализируем тему
        topic, confidence = await analyze_news(message.text)
        if topic:
            news.topic = topic
            news.confidence_level = confidence
            await session.commit()

@router.message(F.photo)
async def handle_photo(message: Message):
    """Обработка фотографий"""
    if str(message.chat.id) not in settings.SOURCE_CHANNEL_IDS:
        return
    
    # Получаем файл фото
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    
    # Сохраняем новость с фото
    async with async_session() as session:
        news = News(
            source_channel_id=str(message.chat.id),
            message_id=message.message_id,
            text=message.caption or "",
            media_path=file.file_path
        )
        session.add(news)
        await session.commit()
        
        # Анализируем тему
        if message.caption:
            topic, confidence = await analyze_news(message.caption)
            if topic:
                news.topic = topic
                news.confidence_level = confidence
                await session.commit() 