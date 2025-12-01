"""Dependency injection container for FastAPI."""

from typing import AsyncGenerator
from fastapi import Depends

from core.config import Settings, get_settings
from core.interfaces import IPokemonRepository, IPokemonService
from core.cache_interface import ICache
from repositories.pokemon_repository import create_pokemon_repository
from repositories.cached_pokemon_repository import CachedPokemonRepository
from services.pokemon_service import create_pokemon_service
from infrastructure.cache_factory import create_cache


async def get_cache(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[ICache, None]:
    """Provide configured cache instance."""
    cache = create_cache(settings)
    
    if hasattr(cache, 'start_cleanup'):
        await cache.start_cleanup()
    
    try:
        yield cache
    finally:
        await cache.close()


async def get_pokemon_repository(
    settings: Settings = Depends(get_settings),
    cache: ICache = Depends(get_cache)
) -> AsyncGenerator[IPokemonRepository, None]:
    """Provide pokemon repository with optional caching."""
    base_repository = create_pokemon_repository(settings)
    
    if settings.cache_enabled:
        repository = CachedPokemonRepository(
            base_repository=base_repository,
            cache=cache,
            default_ttl=settings.cache_ttl
        )
    else:
        repository = base_repository
    
    try:
        yield repository
    finally:
        await repository.close()


async def get_pokemon_service(
    repository: IPokemonRepository = Depends(get_pokemon_repository)
) -> IPokemonService:
    """Provide pokemon service instance."""
    return create_pokemon_service(repository)


class DependencyContainer:
    """Optional singleton container for application-scoped dependencies."""
    
    def __init__(self):
        self._settings: Settings | None = None
        self._repository: IPokemonRepository | None = None
    
    @property
    def settings(self) -> Settings:
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    async def get_repository(self) -> IPokemonRepository:
        """Return singleton repository."""
        if self._repository is None:
            self._repository = create_pokemon_repository(self.settings)
        return self._repository
    
    async def cleanup(self):
        """Clean up resources on shutdown."""
        if self._repository:
            await self._repository.close()


_container: DependencyContainer | None = None


def get_container() -> DependencyContainer:
    """Return singleton dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container
