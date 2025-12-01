"""Centralized application configuration."""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    app_name: str = "Pokemon API Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Google Gemini AI
    google_api_key: str = ""
    
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    pokeapi_timeout: float = 5.0
    pokeapi_max_retries: int = 3
    
    cache_enabled: bool = True
    cache_type: str = "memory"
    cache_ttl: int = 3600
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return singleton settings instance."""
    return Settings()
