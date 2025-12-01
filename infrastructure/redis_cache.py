"""Redis cache implementation."""

import json
from typing import Any, Optional
from core.cache_interface import ICache

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache(ICache):
    """Production-ready cache using Redis.
    
    Requires Redis server and redis-py library.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "pokemon:"
    ):
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis not installed. Install with: pip install redis"
            )
        
        self._key_prefix = key_prefix
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False
        )
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self._key_prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for Redis storage."""
        return json.dumps(value).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from Redis."""
        return json.loads(data.decode('utf-8'))
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self._client.get(self._make_key(key))
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            print(f"Error getting from Redis: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized = self._serialize(value)
            if ttl:
                await self._client.setex(self._make_key(key), ttl, serialized)
            else:
                await self._client.set(self._make_key(key), serialized)
            return True
        except Exception as e:
            print(f"Error setting to Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            result = await self._client.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            print(f"Error deleting from Redis: {e}")
            return False
    
    async def clear(self) -> None:
        try:
            pattern = f"{self._key_prefix}*"
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    await self._client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            print(f"Error clearing Redis: {e}")
    
    async def exists(self, key: str) -> bool:
        try:
            result = await self._client.exists(self._make_key(key))
            return result > 0
        except Exception as e:
            print(f"Error checking existence in Redis: {e}")
            return False
    
    async def close(self) -> None:
        await self._client.close()
