from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session
from ..models import News, DigestLog

router = Router()

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Показать статистику бота"""
    async with async_session() as session:
        # Получаем количество новостей
        news_count = await session.scalar(select(func.count(News.id)))
        
        # Получаем количество дайджестов
        digest_count = await session.scalar(select(func.count(DigestLog.id)))
        
        # Формируем ответ
        response = (
            "📊 Статистика бота:\n\n"
            f"📰 Всего новостей: {news_count}\n"
            f"📨 Отправлено дайджестов: {digest_count}"
        )
        
        await message.answer(response) 