import os
import aiohttp
import structlog
from typing import Optional, List
from aiogram.types import Message
from .config import settings

logger = structlog.get_logger()

class MediaHandler:
    def __init__(self):
        self.media_dir = "media"
        os.makedirs(self.media_dir, exist_ok=True)
    
    async def handle_media(self, message: Message) -> Optional[str]:
        """Обрабатывает медиафайлы из сообщения"""
        try:
            if message.photo:
                # Получаем фото с максимальным разрешением
                photo = message.photo[-1]
                file_id = photo.file_id
                file = await message.bot.get_file(file_id)
                file_path = file.file_path
                
                # Скачиваем файл
                file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as response:
                        if response.status == 200:
                            # Сохраняем файл
                            file_name = f"{file_id}.jpg"
                            file_path = os.path.join(self.media_dir, file_name)
                            with open(file_path, "wb") as f:
                                f.write(await response.read())
                            return file_path
            
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
    
    async def handle_media_group(self, messages: List[Message]) -> List[str]:
        """Обрабатывает группу медиафайлов (альбом)"""
        media_urls = []
        for message in messages:
            if message.media_group_id:
                url = await self.handle_media(message)
                if url:
                    media_urls.append(url)
        return media_urls 