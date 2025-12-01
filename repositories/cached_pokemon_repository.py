"""Cached pokemon repository using Decorator Pattern."""

from typing import Any, Dict
from core.interfaces import IPokemonRepository
from core.cache_interface import ICache


class CachedPokemonRepository(IPokemonRepository):
    """Decorator adding cache to any pokemon repository implementation."""
    
    def __init__(
        self,
        base_repository: IPokemonRepository,
        cache: ICache,
        default_ttl: int = 3600
    ):
        self._base = base_repository
        self._cache = cache
        self._default_ttl = default_ttl
    
    def _make_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate consistent cache key."""
        return f"{prefix}:{identifier.lower()}"
    
    async def get_pokemon(self, name: str) -> Dict[str, Any]:
        cache_key = self._make_cache_key("pokemon", name)
        
        cached_value = await self._cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        result = await self._base.get_pokemon(name)
        await self._cache.set(cache_key, result, ttl=self._default_ttl)
        
        return result
    
    async def list_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        cache_key = self._make_cache_key("pokemons", f"list_{limit}_{offset}")
        
        cached_value = await self._cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        result = await self._base.list_pokemons(limit=limit, offset=offset)
        await self._cache.set(cache_key, result, ttl=300)
        
        return result
    
    async def get_ability(self, name: str) -> Dict[str, Any]:
        cache_key = self._make_cache_key("ability", name)
        
        cached_value = await self._cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        result = await self._base.get_ability(name)
        await self._cache.set(cache_key, result, ttl=self._default_ttl)
        
        return result

    async def get_type(self, name: str) -> Dict[str, Any]:
        cache_key = self._make_cache_key("type", name)
        cached_value = await self._cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        result = await self._base.get_type(name)
        await self._cache.set(cache_key, result, ttl=self._default_ttl)
        return result
    
    async def get_generation(self, name: str) -> Dict[str, Any]:
        """Get generation data by name or ID (cached)."""
        cache_key = self._make_cache_key("generation", name)
        cached_value = await self._cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        result = await self._base.get_generation(name)
        await self._cache.set(cache_key, result, ttl=self._default_ttl)
        return result
    
    async def close(self) -> None:
        await self._cache.close()
        await self._base.close()
    
    async def invalidate_pokemon(self, name: str) -> bool:
        """Invalidate cached pokemon data."""
        cache_key = self._make_cache_key("pokemon", name)
        return await self._cache.delete(cache_key)
    
    async def clear_cache(self) -> None:
        """Clear all cached data."""
        await self._cache.clear()
