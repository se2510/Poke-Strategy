"""Service abstractions following Dependency Inversion Principle."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IPokemonRepository(ABC):
    """Pokemon repository interface."""
    
    @abstractmethod
    async def get_pokemon(self, name: str) -> Dict[str, Any]:
        """Get pokemon by name."""
        pass
    
    @abstractmethod
    async def list_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """List pokemons with pagination."""
        pass
    
    @abstractmethod
    async def get_ability(self, name: str) -> Dict[str, Any]:
        """Get ability by name."""
        pass

    @abstractmethod
    async def get_type(self, name: str) -> Dict[str, Any]:
        """Get type data by name."""
        pass
    
    @abstractmethod
    async def get_generation(self, name: str) -> Dict[str, Any]:
        """Get generation data by name or ID."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close repository connections."""
        pass


class IPokemonService(ABC):
    """Pokemon business logic service interface."""
    
    @abstractmethod
    async def get_pokemon_info(self, name: str) -> Dict[str, Any]:
        """Get enriched pokemon information."""
        pass
    
    @abstractmethod
    async def search_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search pokemons with filters."""
        pass
