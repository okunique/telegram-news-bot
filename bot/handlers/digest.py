from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session
from ..models import News, DigestLog
from ..config import settings

router = Router()

@router.message(Command("digest"))
async def cmd_digest(message: Message):
    """Сформировать дайджест новостей"""
    async with async_session() as session:
        # Получаем новости за последние 24 часа
        yesterday = datetime.utcnow() - timedelta(days=1)
        news = await session.scalars(
            select(News)
            .where(News.timestamp >= yesterday)
            .order_by(News.timestamp.desc())
        )
        
        if not news:
            await message.answer("За последние 24 часа новостей не найдено")
            return
        
        # Группируем новости по темам
        topics = {}
        for item in news:
            if item.topic:
                if item.topic not in topics:
                    topics[item.topic] = []
                topics[item.topic].append(item)
        
        # Формируем дайджест
        digest = "📰 Дайджест новостей за 24 часа:\n\n"
        
        for topic, items in topics.items():
            digest += f"📌 {topic}:\n"
            for item in items[:3]:  # Берем только 3 последние новости по теме
                digest += f"• {item.text[:100]}...\n"
            digest += "\n"
        
        # Сохраняем лог дайджеста
        log = DigestLog(
            period="24h",
            news_count=len(news),
            topics_count=len(topics)
        )
        session.add(log)
        await session.commit()
        
        await message.answer(digest) 