from typing import Optional, List
from telegram import Update
from telegram.ext import ContextTypes
import aiohttp
import structlog
from .config import settings

logger = structlog.get_logger()

class MediaHandler:
    def __init__(self):
        self.supported_types = ["photo", "document", "video"]
    
    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Обрабатывает медиафайлы из сообщения и возвращает URL для сохранения"""
        try:
            if update.message.photo:
                # Берем последнее фото (самое большое разрешение)
                photo = update.message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                return file.file_path
            
            elif update.message.document:
                file = await context.bot.get_file(update.message.document.file_id)
                return file.file_path
            
            elif update.message.video:
                file = await context.bot.get_file(update.message.video.file_id)
                return file.file_path
            
            return None
            
        except Exception as e:
            logger.error("Error handling media", error=str(e))
            return None
    
    async def download_media(self, file_path: str) -> Optional[bytes]:
        """Скачивает медиафайл по URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_path) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error("Failed to download media", 
                                   status=response.status)
                        return None
        except Exception as e:
            logger.error("Error downloading media", error=str(e))
            return None
    
    async def handle_media_group(self, updates: List[Update], context: ContextTypes.DEFAULT_TYPE) -> List[str]:
        """Обрабатывает группу медиафайлов (альбом)"""
        media_urls = []
        for update in updates:
            if update.message.media_group_id:
                url = await self.handle_media(update, context)
                if url:
                    media_urls.append(url)
        return media_urls 