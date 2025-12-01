"""Pokemon repository implementation using PokeAPI.

This module implements the IPokemonRepository interface using
the external PokeAPI as a data source.
"""

from typing import Any, Dict
import httpx
import asyncio

from core.interfaces import IPokemonRepository
from core.config import Settings
from core.exceptions import ExternalAPIError, ResourceNotFoundError


class PokeAPIRepository(IPokemonRepository):
    """Repository that connects to PokeAPI.
    
    Implements automatic retries and error handling.
    Dependencies (config) are injected into the constructor.
    """
    
    def __init__(self, settings: Settings):
        """Initialize repository with injected configuration.
        
        Args:
            settings: Application configuration (injected)
        """
        self.base_url = settings.pokeapi_base_url.rstrip("/")
        self.timeout = settings.pokeapi_timeout
        self.max_retries = settings.pokeapi_max_retries
        self._client = httpx.AsyncClient(timeout=self.timeout)
    
    async def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Perform GET request with automatic retries."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        backoff = 0.3
        
        for attempt in range(self.max_retries):
            try:
                resp = await self._client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code if e.response else None
                
                # Handle 404 specifically
                if status == 404:
                    # Extract resource name from path
                    resource_parts = path.split('/')
                    resource_type = resource_parts[0] if resource_parts else "Resource"
                    resource_id = resource_parts[-1] if len(resource_parts) > 1 else path
                    raise ResourceNotFoundError(
                        resource_type=resource_type.capitalize(),
                        resource_id=resource_id
                    ) from e
                
                # Retry on transient errors
                if status in (429, 500, 502, 503, 504) and attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                
                text = e.response.text if e.response else ""
                raise ExternalAPIError(
                    message=f"HTTP {status}: {text}",
                    api_name="PokeAPI",
                    status_code=status,
                    original_error=e
                ) from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise ExternalAPIError(
                    message=f"Request failed: {e}",
                    api_name="PokeAPI",
                    original_error=e
                ) from e
        
        raise ExternalAPIError(
            message="Max retries exceeded",
            api_name="PokeAPI"
        )
    
    async def get_pokemon(self, name: str) -> Dict[str, Any]:
        """Implement IPokemonRepository.get_pokemon."""
        return await self._get(f"pokemon/{name.lower()}")
    
    async def list_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Implement IPokemonRepository.list_pokemons."""
        return await self._get("pokemon", params={"limit": limit, "offset": offset})
    
    async def get_ability(self, name: str) -> Dict[str, Any]:
        """Implement IPokemonRepository.get_ability."""
        return await self._get(f"ability/{name.lower()}")

    async def get_type(self, name: str) -> Dict[str, Any]:
        return await self._get(f"type/{name.lower()}")
    
    async def get_generation(self, name: str) -> Dict[str, Any]:
        """Get generation data by name or ID."""
        return await self._get(f"generation/{name.lower()}")
    
    async def close(self) -> None:
        """Implement IPokemonRepository.close."""
        await self._client.aclose()


# Factory function to create repository
def create_pokemon_repository(settings: Settings) -> IPokemonRepository:
    """Factory to create repository instances.
    
    Args:
        settings: Application configuration
        
    Returns:
        IPokemonRepository implementation
    """
    return PokeAPIRepository(settings)
