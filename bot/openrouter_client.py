import aiohttp
from typing import Dict, Any, Optional
from .config import settings
import structlog

logger = structlog.get_logger()

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализирует текст и возвращает тематику, важность и другие параметры"""
        prompt = f"""
        Проанализируй следующий текст новости и определи:
        1. Тематику (из списка: {', '.join(settings.TRADFI_TOPICS + settings.CRYPTO_TOPICS)})
        2. Целевую рыночную область (TradFi, Crypto или Both)
        3. Важность (от 1 до 5)
        4. Является ли катализатором (True/False)
        
        Текст: {text}
        
        Ответ дай в формате JSON.
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "anthropic/claude-3-opus-20240229",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error("OpenRouter API error", 
                                   status=response.status,
                                   text=await response.text())
                        return None
            except Exception as e:
                logger.error("OpenRouter API request failed", error=str(e))
                return None
    
    async def translate_text(self, text: str, style: str = "business") -> Optional[str]:
        """Переводит текст на русский язык с учетом стиля"""
        prompt = f"""
        Переведи следующий текст на русский язык, используя {style} стиль:
        
        {text}
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "anthropic/claude-3-opus-20240229",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error("OpenRouter API translation error",
                                   status=response.status,
                                   text=await response.text())
                        return None
            except Exception as e:
                logger.error("OpenRouter API translation request failed", error=str(e))
                return None 