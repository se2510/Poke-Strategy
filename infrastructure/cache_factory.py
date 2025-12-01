"""Factory to create cache instances based on configuration."""

from core.cache_interface import ICache
from core.config import Settings
from infrastructure.memory_cache import InMemoryCache


def create_cache(settings: Settings) -> ICache:
    """Create cache implementation based on settings.
    
    Args:
        settings: Application configuration
        
    Returns:
        ICache implementation
        
    Raises:
        ValueError: If cache_type is not supported
    """
    if not settings.cache_enabled:
        return NullCache()
    
    cache_type = settings.cache_type.lower()
    
    if cache_type == "memory":
        return InMemoryCache(cleanup_interval=60)
    
    elif cache_type == "redis":
        try:
            from infrastructure.redis_cache import RedisCache
            return RedisCache(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                key_prefix="pokemon:"
            )
        except ImportError:
            raise ValueError(
                "Redis cache requires: pip install redis"
            )
    
    else:
        raise ValueError(
            f"Unsupported cache type: {cache_type}. "
            f"Use 'memory' or 'redis'"
        )


class NullCache(ICache):
    """No-op cache implementation for testing or when caching is disabled."""
    
    async def get(self, key: str):
        return None
    
    async def set(self, key: str, value, ttl=None) -> bool:
        return True
    
    async def delete(self, key: str) -> bool:
        return False
    
    async def clear(self) -> None:
        pass
    
    async def exists(self, key: str) -> bool:
        return False
    
    async def close(self) -> None:
        pass
