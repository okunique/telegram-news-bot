import aiohttp
import logging
import json
from typing import Tuple, Optional, Dict
from .config import settings

logger = logging.getLogger(__name__)

async def analyze_news(text: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Анализирует текст новости и определяет её тему
    
    Args:
        text: Текст новости для анализа
        
    Returns:
        Tuple[Optional[str], Optional[float]]: Тема новости и уровень уверенности
    """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Формируем промпт для анализа
            prompt = f"""
            Проанализируй следующий текст новости и определи:
            1. Тематику (из списка: {', '.join(settings.TRADFI_TOPICS + settings.CRYPTO_TOPICS)})
            2. Уровень уверенности в определении темы (от 0 до 1)
            
            Текст новости:
            {text}
            
            Ответ должен быть в формате:
            Тема: [тема]
            Уверенность: [число от 0 до 1]
            """
            
            data = {
                "model": settings.OPENROUTER_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    logger.error(f"Ошибка API OpenRouter: {response.status}")
                    return None, None
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Парсим ответ
                topic = None
                confidence = None
                
                for line in content.split("\n"):
                    if line.startswith("Тема:"):
                        topic = line.replace("Тема:", "").strip()
                    elif line.startswith("Уверенность:"):
                        try:
                            confidence = float(line.replace("Уверенность:", "").strip())
                        except ValueError:
                            confidence = None
                
                return topic, confidence
                
    except Exception as e:
        logger.error(f"Ошибка при анализе новости: {e}")
        return None, None

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_text(self, text: str) -> Tuple[Optional[str], Optional[float]]:
        """Анализирует текст и возвращает тематику, важность и другие параметры"""
        prompt = f"""
        Проанализируй следующий текст новости и определи:
        1. Тематику (из списка: {', '.join(settings.TRADFI_TOPICS + settings.CRYPTO_TOPICS)})
        2. Уровень уверенности в определении темы (от 0 до 1)
        
        Текст новости:
        {text}
        
        Ответ должен быть в формате:
        Тема: [тема]
        Уверенность: [число от 0 до 1]
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
                        content = result["choices"][0]["message"]["content"]
                        
                        # Парсим ответ
                        topic = None
                        confidence = None
                        
                        for line in content.split("\n"):
                            if line.startswith("Тема:"):
                                topic = line.replace("Тема:", "").strip()
                            elif line.startswith("Уверенность:"):
                                try:
                                    confidence = float(line.replace("Уверенность:", "").strip())
                                except ValueError:
                                    confidence = None
                        
                        return topic, confidence
                    else:
                        logger.error("OpenRouter API error", 
                                   status=response.status,
                                   text=await response.text())
                        return None, None
            except Exception as e:
                logger.error("OpenRouter API request failed", error=str(e))
                return None, None
    
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

async def analyze_news_full(text: str) -> Dict:
    """
    Расширенный анализ новости
    
    Returns:
        Dict с полями:
        - topic: тема новости
        - confidence: уверенность (0-1)
        - importance: важность (1-5)
        - is_catalyst: является ли катализатором
        - market_target: TradFi/Crypto/Both
    """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Проанализируй следующую новость и определи:
            1. Тематику (из списка: {', '.join(settings.TRADFI_TOPICS + settings.CRYPTO_TOPICS)})
            2. Уровень уверенности в определении темы (от 0 до 1)
            3. Важность новости (от 1 до 5, где 5 - максимально важная)
            4. Является ли новость катализатором рынка (True/False)
            5. Целевая рыночная область (TradFi/Crypto/Both)
            
            Текст новости:
            {text}
            
            Ответ должен быть в формате JSON:
            {{
                "topic": "тема",
                "confidence": 0.95,
                "importance": 4,
                "is_catalyst": true,
                "market_target": "TradFi"
            }}
            """
            
            data = {
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with session.post(
                f"{settings.OPENROUTER_API_URL}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    logger.error(f"Ошибка API OpenRouter: {response.status}")
                    return None
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    analysis = json.loads(content)
                    return analysis
                except json.JSONDecodeError:
                    logger.error("Ошибка парсинга JSON ответа")
                    return None
                
    except Exception as e:
        logger.error(f"Ошибка при анализе новости: {e}")
        return None

async def translate_news(text: str, style: str = "business") -> Optional[str]:
    """
    Переводит новость на русский язык с учетом стиля
    
    Args:
        text: Текст для перевода
        style: Стиль перевода (business, technical, journalistic)
    """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Переведи следующий текст на русский язык, используя {style} стиль.
            Сохрани все термины и специфические выражения.
            
            Текст:
            {text}
            """
            
            data = {
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with session.post(
                f"{settings.OPENROUTER_API_URL}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    logger.error(f"Ошибка API OpenRouter при переводе: {response.status}")
                    return None
                
                result = await response.json()
                return result["choices"][0]["message"]["content"]
                
    except Exception as e:
        logger.error(f"Ошибка при переводе новости: {e}")
        return None 