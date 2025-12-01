"""In-memory cache implementation using dictionary."""

import asyncio
import time
from typing import Any, Dict, Optional, Tuple
from core.cache_interface import ICache


class InMemoryCache(ICache):
    """In-memory cache with TTL support.
    
    Suitable for development, testing, and small-scale applications.
    Not shared between processes or persistent across restarts.
    """
    
    def __init__(self, cleanup_interval: int = 60):
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._lock = asyncio.Lock()
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        self._hits: int = 0
        self._misses: int = 0
        
    async def start_cleanup(self):
        """Start periodic cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Periodically clean expired entries."""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self._cleanup_expired()
    
    async def _cleanup_expired(self):
        """Remove expired entries."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry is not None and expiry < current_time
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def _is_expired(self, expiry: Optional[float]) -> bool:
        """Check if entry has expired."""
        if expiry is None:
            return False
        return expiry < time.time()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            value, expiry = self._cache[key]
            
            if self._is_expired(expiry):
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        async with self._lock:
            expiry = None
            if ttl is not None:
                expiry = time.time() + ttl
            
            self._cache[key] = (value, expiry)
            return True
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
    
    async def exists(self, key: str) -> bool:
        async with self._lock:
            if key not in self._cache:
                return False
            
            _, expiry = self._cache[key]
            if self._is_expired(expiry):
                del self._cache[key]
                return False
            
            return True
    
    async def close(self) -> None:
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        await self.clear()
    
    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests) if total_requests else 0.0
        return {
            "size": self.size(),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
        }
