from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = Field(default=os.getenv("TELEGRAM_BOT_TOKEN", ""))
    SOURCE_CHANNEL_IDS: List[str] = Field(
        default=[x.strip() for x in os.getenv("SOURCE_CHANNEL_IDS", "").split(",") if x.strip()]
    )
    TARGET_CHANNEL_ID: str = Field(default=os.getenv("TARGET_CHANNEL_ID", ""))
    
    # OpenRouter settings
    OPENROUTER_API_KEY: str = Field(default=os.getenv("OPENROUTER_API_KEY", ""))
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1"
    
    # Database settings
    POSTGRES_HOST: str = Field(default=os.getenv("POSTGRES_HOST", "localhost"))
    POSTGRES_PORT: int = Field(default=int(os.getenv("POSTGRES_PORT", "5432")))
    POSTGRES_DB: str = Field(default=os.getenv("POSTGRES_DB", "newsbot"))
    POSTGRES_USER: str = Field(default=os.getenv("POSTGRES_USER", ""))
    POSTGRES_PASSWORD: str = Field(default=os.getenv("POSTGRES_PASSWORD", ""))
    
    # Market settings
    TRADFI_TOPICS: List[str] = ["экономика", "геополитика", "энергетика", "политика"]
    CRYPTO_TOPICS: List[str] = ["криптовалюты", "DeFi", "Web3", "NFT"]
    
    # Digest settings
    DIGEST_PERIODS: List[str] = ["1h", "24h"]
    
    class Config:
        env_file = ".env"

settings = Settings() 