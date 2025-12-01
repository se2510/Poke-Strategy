"""Cache system unit tests."""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any
from infrastructure.memory_cache import InMemoryCache
from repositories.cached_pokemon_repository import CachedPokemonRepository
from core.interfaces import IPokemonRepository


class MockPokemonRepository(IPokemonRepository):
    """Mock repository for testing."""
    
    def __init__(self):
        self._get_pokemon_mock = AsyncMock()
        self._list_pokemons_mock = AsyncMock()
        self._get_ability_mock = AsyncMock()
        self._get_type_mock = AsyncMock()
        self._get_generation_mock = AsyncMock()
        self._close_mock = AsyncMock()
    
    async def get_pokemon(self, name: str) -> Dict[str, Any]:
        return await self._get_pokemon_mock(name)
    
    async def list_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._list_pokemons_mock(limit, offset)
    
    async def get_ability(self, name: str) -> Dict[str, Any]:
        return await self._get_ability_mock(name)
    
    async def get_type(self, name: str) -> Dict[str, Any]:
        return await self._get_type_mock(name)
    
    async def get_generation(self, name: str) -> Dict[str, Any]:
        return await self._get_generation_mock(name)
    
    async def close(self) -> None:
        await self._close_mock()


@pytest.fixture
async def cache():
    """Provide in-memory cache."""
    cache = InMemoryCache()
    await cache.start_cleanup()
    yield cache
    await cache.close()


@pytest.fixture
def mock_repository():
    """Provide mock repository."""
    return MockPokemonRepository()


@pytest.fixture
def cached_repository(mock_repository, cache):
    """Provide cached repository."""
    return CachedPokemonRepository(
        base_repository=mock_repository,
        cache=cache,
        default_ttl=60
    )


@pytest.mark.asyncio
async def test_cache_stores_and_retrieves(cache):
    """Test: cache stores and retrieves values."""
    # Arrange
    key = "test_key"
    value = {"data": "test_value"}
    
    # Act
    await cache.set(key, value, ttl=60)
    result = await cache.get(key)
    
    # Assert
    assert result == value


@pytest.mark.asyncio
async def test_cache_returns_none_for_missing_key(cache):
    """Test: cache returns None for nonexistent keys."""
    result = await cache.get("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_ttl_expiration(cache):
    """Test: entries expire after TTL."""
    # Arrange
    key = "expiring_key"
    value = {"data": "will_expire"}
    
    # Act
    await cache.set(key, value, ttl=1)  # 1 second
    
    # Verify it exists immediately
    assert await cache.exists(key)
    
    # Wait for expiration
    import asyncio
    await asyncio.sleep(1.1)
    
    # Assert
    assert not await cache.exists(key)
    assert await cache.get(key) is None


@pytest.mark.asyncio
async def test_cache_delete(cache):
    """Test: delete cache entries."""
    # Arrange
    key = "deletable_key"
    await cache.set(key, {"data": "value"})
    
    # Act
    deleted = await cache.delete(key)
    
    # Assert
    assert deleted is True
    assert await cache.get(key) is None


@pytest.mark.asyncio
async def test_cache_clear(cache):
    """Test: clear entire cache."""
    # Arrange
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    
    # Act
    await cache.clear()
    
    # Assert
    assert await cache.get("key1") is None
    assert await cache.get("key2") is None


@pytest.mark.asyncio
async def test_cached_repository_uses_cache_on_second_call(cached_repository, mock_repository):
    """Test: cached repository uses cache on subsequent calls."""
    # Arrange
    pokemon_data = {"name": "pikachu", "id": 25}
    mock_repository._get_pokemon_mock.return_value = pokemon_data
    
    # Act - First call (should go to repository)
    result1 = await cached_repository.get_pokemon("pikachu")
    
    # Act - Second call (should come from cache)
    result2 = await cached_repository.get_pokemon("pikachu")
    
    # Assert
    assert result1 == pokemon_data
    assert result2 == pokemon_data
    # Base repository should only be called once
    mock_repository._get_pokemon_mock.assert_called_once_with("pikachu")


@pytest.mark.asyncio
async def test_cached_repository_bypasses_cache_on_different_keys(cached_repository, mock_repository):
    """Test: different keys don't use the same cache."""
    # Arrange
    pikachu_data = {"name": "pikachu", "id": 25}
    bulbasaur_data = {"name": "bulbasaur", "id": 1}
    
    mock_repository._get_pokemon_mock.side_effect = [pikachu_data, bulbasaur_data]
    
    # Act
    result1 = await cached_repository.get_pokemon("pikachu")
    result2 = await cached_repository.get_pokemon("bulbasaur")
    
    # Assert
    assert result1 == pikachu_data
    assert result2 == bulbasaur_data
    assert mock_repository._get_pokemon_mock.call_count == 2


@pytest.mark.asyncio
async def test_cached_repository_invalidate(cached_repository, mock_repository, cache):
    """Test: invalidate cache for a specific Pokemon."""
    # Arrange
    pokemon_data = {"name": "pikachu", "id": 25}
    updated_data = {"name": "pikachu", "id": 25, "level": 50}
    
    mock_repository._get_pokemon_mock.side_effect = [pokemon_data, updated_data]
    
    # Act - First call
    result1 = await cached_repository.get_pokemon("pikachu")
    
    # Invalidate cache
    await cached_repository.invalidate_pokemon("pikachu")
    
    # Second call (should go to repository again)
    result2 = await cached_repository.get_pokemon("pikachu")
    
    # Assert
    assert result1 == pokemon_data
    assert result2 == updated_data
    assert mock_repository._get_pokemon_mock.call_count == 2


@pytest.mark.asyncio
async def test_memory_cache_size(cache):
    """Test: verify cache size."""
    # Arrange & Act
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    
    # Assert
    assert cache.size() == 3
    
    # Delete one
    await cache.delete("key2")
    assert cache.size() == 2
