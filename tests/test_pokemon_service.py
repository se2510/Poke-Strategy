"""Unit tests for PokemonService demonstrating dependency injection benefits."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from services.pokemon_service import PokemonService
from core.interfaces import IPokemonRepository
from core.exceptions import ValidationError


class MockPokemonRepository(IPokemonRepository):
    """Mock repository for testing."""
    
    def __init__(self):
        self._get_pokemon_mock = AsyncMock()
        self._list_pokemons_mock = AsyncMock()
        self._get_ability_mock = AsyncMock()
        self._get_type_mock = AsyncMock()
        self._get_generation_mock = AsyncMock()
        self._close_mock = AsyncMock()
    
    async def get_pokemon(self, name: str):
        return await self._get_pokemon_mock(name)
    
    async def list_pokemons(self, limit: int = 20, offset: int = 0):
        return await self._list_pokemons_mock(limit=limit, offset=offset)
    
    async def get_ability(self, name: str):
        return await self._get_ability_mock(name)
    
    async def get_type(self, name: str):
        return await self._get_type_mock(name)
    
    async def get_generation(self, name: str):
        return await self._get_generation_mock(name)
    
    async def close(self):
        return await self._close_mock()


@pytest.fixture
def mock_repository():
    """Provide mock repository."""
    return MockPokemonRepository()


@pytest.fixture
def pokemon_service(mock_repository):
    """Provide service with injected mock repository."""
    return PokemonService(pokemon_repository=mock_repository)


@pytest.mark.asyncio
async def test_get_pokemon_info_success(pokemon_service, mock_repository):
    """Test: get Pokemon information successfully."""
    # Arrange
    expected_data = {
        "name": "pikachu",
        "id": 25,
        "types": [{"type": {"name": "electric"}}]
    }
    mock_repository._get_pokemon_mock.return_value = expected_data
    
    # Act
    result = await pokemon_service.get_pokemon_info("pikachu")
    
    # Assert
    assert result == expected_data
    mock_repository._get_pokemon_mock.assert_called_once_with("pikachu")


@pytest.mark.asyncio
async def test_get_pokemon_info_empty_name(pokemon_service):
    """Test: error when name is empty."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        await pokemon_service.get_pokemon_info("")


@pytest.mark.asyncio
async def test_search_pokemons_with_valid_params(pokemon_service, mock_repository):
    """Test: search pokemons with valid parameters."""
    expected_data = {
        "count": 1000,
        "results": [{"name": "bulbasaur"}, {"name": "ivysaur"}]
    }
    mock_repository._list_pokemons_mock.return_value = expected_data
    
    result = await pokemon_service.search_pokemons(limit=20, offset=0)
    
    assert result == expected_data
    mock_repository._list_pokemons_mock.assert_called_once()


@pytest.mark.asyncio
async def test_search_pokemons_invalid_limit(pokemon_service):
    """Test: error when limit is invalid."""
    with pytest.raises(ValidationError, match="must be between"):
        await pokemon_service.search_pokemons(limit=0)
    
    with pytest.raises(ValidationError, match="must be between"):
        await pokemon_service.search_pokemons(limit=101)


@pytest.mark.asyncio
async def test_search_pokemons_invalid_offset(pokemon_service):
    """Test: error when offset is negative."""
    with pytest.raises(ValidationError, match="cannot be negative"):
        await pokemon_service.search_pokemons(offset=-1)


@pytest.mark.asyncio
async def test_get_pokemon_summary(pokemon_service, mock_repository):
    """Test: generate compact summary of a Pokemon."""
    # Arrange: simulated large object (only used fields)
    large_payload = {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "base_experience": 112,
        "types": [
            {"type": {"name": "electric"}}
        ],
        "abilities": [
            {"ability": {"name": "static"}},
            {"ability": {"name": "lightning-rod"}}
        ],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 35},
            {"stat": {"name": "attack"}, "base_stat": 55},
            {"stat": {"name": "defense"}, "base_stat": 40},
        ],
        "moves": [
            {"move": {"name": "thunderbolt"}},
            {"move": {"name": "quick-attack"}},
            {"move": {"name": "iron-tail"}},
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
        },
        "is_default": True,
        "forms": [
            {"name": "pikachu"}
        ],
        "order": 35,
    }
    mock_repository._get_pokemon_mock.return_value = large_payload

    # Act
    summary = await pokemon_service.get_pokemon_summary("pikachu")

    # Assert: essential keys present and reduced
    assert summary["name"] == "pikachu"
    assert summary["id"] == 25
    assert summary["types"] == ["electric"]
    assert summary["abilities"] == ["static", "lightning-rod"]
    assert summary["stats"]["attack"] == 55
    assert summary["moves_sample"][:2] == ["thunderbolt", "quick-attack"]
    assert summary["moves_count"] == 3
    assert "sprite" in summary
    # Confirm it didn't include the original giant "moves" field
    assert "moves" not in summary


@pytest.mark.asyncio
async def test_get_type_summary(pokemon_service, mock_repository):
    mock_repository._get_type_mock.return_value = {
        "pokemon": [
            {"pokemon": {"name": "pikachu"}},
            {"pokemon": {"name": "raichu"}},
        ]
    }
    mock_repository._get_pokemon_mock.side_effect = [
        {"id": 25, "name": "pikachu", "types": [{"type": {"name": "electric"}},], "abilities": [], "stats": [], "moves": []},
        {"id": 26, "name": "raichu", "types": [{"type": {"name": "electric"}},], "abilities": [], "stats": [], "moves": []},
    ]
    result = await pokemon_service.get_type_summary("electric", limit=2)
    assert result["type"] == "electric"
    assert result["returned"] == 2


@pytest.mark.asyncio
async def test_compare_pokemons(pokemon_service, mock_repository):
    # Mock summaries via underlying calls
    mock_repository._get_pokemon_mock.side_effect = [
        {"id": 25, "name": "pikachu", "types": [{"type": {"name": "electric"}}], "abilities": [], "stats": [{"stat": {"name": "attack"}, "base_stat": 55}], "moves": []},
        {"id": 1, "name": "bulbasaur", "types": [{"type": {"name": "grass"}}], "abilities": [], "stats": [{"stat": {"name": "attack"}, "base_stat": 49}], "moves": []},
    ]
    diff = await pokemon_service.compare_pokemons("pikachu", "bulbasaur")
    assert diff["comparison"]["higher_attack"] == "pikachu"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_get_pokemon():
    """Integration test with real API (requires network connection)."""
    from core.config import Settings
    from repositories.pokemon_repository import create_pokemon_repository
    
    settings = Settings()
    repository = create_pokemon_repository(settings)
    service = PokemonService(pokemon_repository=repository)
    
    try:
        result = await service.get_pokemon_info("pikachu")
        assert result["name"] == "pikachu"
        assert result["id"] == 25
    finally:
        await repository.close()


@pytest.mark.asyncio
async def test_analyze_personality_from_starters_success(pokemon_service, mock_repository):
    """Test personality analysis with valid preferences."""
    # Mock starter pokemon data
    mock_repository._get_pokemon_mock.return_value = {
        "id": 4,
        "name": "charmander",
        "types": [{"type": {"name": "fire"}}],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 39},
            {"stat": {"name": "attack"}, "base_stat": 52},
            {"stat": {"name": "defense"}, "base_stat": 43},
            {"stat": {"name": "special-attack"}, "base_stat": 60},
            {"stat": {"name": "special-defense"}, "base_stat": 50},
            {"stat": {"name": "speed"}, "base_stat": 65}
        ],
        "abilities": [],
        "moves": []
    }
    
    preferences = {
        "battle_style": "aggressive",
        "preferred_stat": "speed",
        "element_preference": "fire"
    }
    
    result = await pokemon_service.analyze_personality_from_starters(preferences)
    
    assert "matched_starter" in result
    assert "personality_traits" in result
    assert "trait_analysis" in result
    assert "summary" in result
    assert isinstance(result["personality_traits"], list)
    assert len(result["personality_traits"]) > 0


@pytest.mark.asyncio
async def test_analyze_personality_empty_preferences(pokemon_service):
    """Test personality analysis with empty preferences."""
    with pytest.raises(ValidationError) as exc_info:
        await pokemon_service.analyze_personality_from_starters({})
    assert "cannot be empty" in exc_info.value.message


@pytest.mark.asyncio
async def test_analyze_personality_balanced_style(pokemon_service, mock_repository):
    """Test personality analysis with balanced battle style."""
    mock_repository._get_pokemon_mock.return_value = {
        "id": 1,
        "name": "bulbasaur",
        "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 45},
            {"stat": {"name": "attack"}, "base_stat": 49},
            {"stat": {"name": "defense"}, "base_stat": 49},
            {"stat": {"name": "special-attack"}, "base_stat": 65},
            {"stat": {"name": "special-defense"}, "base_stat": 65},
            {"stat": {"name": "speed"}, "base_stat": 45}
        ],
        "abilities": [],
        "moves": []
    }
    
    preferences = {
        "battle_style": "balanced",
        "preferred_stat": "hp",
        "element_preference": "any"
    }
    
    result = await pokemon_service.analyze_personality_from_starters(preferences)
    
    assert result["matched_starter"] is not None
    assert "alternative_matches" in result
    assert len(result["alternative_matches"]) <= 3
