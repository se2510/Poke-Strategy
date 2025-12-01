"""Tests for Pokémon utility functions (grouping, classification, team analysis)."""

import pytest
from unittest.mock import AsyncMock, Mock
from services.pokemon_service import PokemonService
from core.exceptions import ValidationError


@pytest.fixture
def mock_repository():
    """Create a mock repository for testing."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def pokemon_service(mock_repository):
    """Create a PokemonService instance with mock repository."""
    return PokemonService(mock_repository)


class TestGroupingUtilities:
    """Test grouping and classification utilities."""
    
    @pytest.mark.asyncio
    async def test_group_pokemons_by_type_success(self, pokemon_service):
        """Test grouping Pokémon by primary type."""
        # Mock get_pokemon_summary to return test data
        async def mock_summary(name):
            summaries = {
                "pikachu": {
                    "name": "pikachu",
                    "types": ["electric"],
                    "stats": {"hp": 35, "attack": 55, "defense": 40}
                },
                "charmander": {
                    "name": "charmander",
                    "types": ["fire"],
                    "stats": {"hp": 39, "attack": 52, "defense": 43}
                },
                "squirtle": {
                    "name": "squirtle",
                    "types": ["water"],
                    "stats": {"hp": 44, "attack": 48, "defense": 65}
                }
            }
            return summaries[name]
        
        pokemon_service.get_pokemon_summary = AsyncMock(side_effect=mock_summary)
        
        result = await pokemon_service.group_pokemons_by_type(
            ["pikachu", "charmander", "squirtle"]
        )
        
        assert "groups" in result
        assert "markdown" in result
        assert result["total_pokemons"] == 3
        assert result["type_count"] == 3
        assert "electric" in result["groups"]
        assert "fire" in result["groups"]
        assert "water" in result["groups"]
        assert "pikachu" in result["groups"]["electric"]
        assert "# Pokémon Grouped by Primary Type" in result["markdown"]
    
    @pytest.mark.asyncio
    async def test_group_pokemons_by_type_empty_list(self, pokemon_service):
        """Test grouping with empty list raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            await pokemon_service.group_pokemons_by_type([])
    
    @pytest.mark.asyncio
    async def test_classify_by_role_success(self, pokemon_service):
        """Test classifying Pokémon by battle role."""
        async def mock_summary(name):
            summaries = {
                "blissey": {
                    "name": "blissey",
                    "types": ["normal"],
                    "stats": {
                        "hp": 255,
                        "attack": 10,
                        "defense": 10,
                        "special-attack": 75,
                        "special-defense": 135,
                        "speed": 55
                    }
                },
                "mewtwo": {
                    "name": "mewtwo",
                    "types": ["psychic"],
                    "stats": {
                        "hp": 106,
                        "attack": 110,
                        "defense": 90,
                        "special-attack": 154,
                        "special-defense": 90,
                        "speed": 130
                    }
                },
                "electrode": {
                    "name": "electrode",
                    "types": ["electric"],
                    "stats": {
                        "hp": 60,
                        "attack": 50,
                        "defense": 70,
                        "special-attack": 80,
                        "special-defense": 80,
                        "speed": 150
                    }
                }
            }
            return summaries[name]
        
        pokemon_service.get_pokemon_summary = AsyncMock(side_effect=mock_summary)
        
        result = await pokemon_service.classify_by_role(
            ["blissey", "mewtwo", "electrode"]
        )
        
        assert "roles" in result
        assert "markdown" in result
        assert "tank" in result["roles"]
        assert "attacker" in result["roles"]
        assert "fast" in result["roles"]
        assert "blissey" in result["roles"]["tank"]
        assert "mewtwo" in result["roles"]["attacker"]
        assert "electrode" in result["roles"]["fast"]


class TestTeamAnalysis:
    """Test team strength and recommendation utilities."""
    
    @pytest.mark.asyncio
    async def test_calculate_team_strength_success(self, pokemon_service):
        """Test team strength calculation."""
        async def mock_summary(name):
            summaries = {
                "pikachu": {
                    "name": "pikachu",
                    "types": ["electric"],
                    "stats": {
                        "hp": 35,
                        "attack": 55,
                        "defense": 40,
                        "special-attack": 50,
                        "special-defense": 50,
                        "speed": 90
                    }
                },
                "charizard": {
                    "name": "charizard",
                    "types": ["fire", "flying"],
                    "stats": {
                        "hp": 78,
                        "attack": 84,
                        "defense": 78,
                        "special-attack": 109,
                        "special-defense": 85,
                        "speed": 100
                    }
                }
            }
            return summaries[name]
        
        pokemon_service.get_pokemon_summary = AsyncMock(side_effect=mock_summary)
        
        result = await pokemon_service.calculate_team_strength(
            ["pikachu", "charizard"]
        )
        
        assert "team" in result
        assert result["team_size"] == 2
        assert "type_coverage" in result
        assert "average_stats" in result
        assert "explanation" in result
        assert "strengths" in result
        assert "recommendations" in result
        assert "electric" in result["type_coverage"]
        assert "fire" in result["type_coverage"]
        assert result["average_stats"]["hp"] > 0
    
    @pytest.mark.asyncio
    async def test_calculate_team_strength_empty_list(self, pokemon_service):
        """Test team strength with empty list raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            await pokemon_service.calculate_team_strength([])
    
    @pytest.mark.asyncio
    async def test_calculate_team_strength_exceeds_limit(self, pokemon_service):
        """Test team strength with more than 6 Pokémon raises error."""
        with pytest.raises(ValidationError, match="cannot exceed 6"):
            await pokemon_service.calculate_team_strength(
                ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
            )
    
    @pytest.mark.asyncio
    async def test_recommend_team_for_battle_success(self, pokemon_service):
        """Test team recommendation for battle."""
        async def mock_summary(name):
            return {
                "name": name,
                "types": ["electric"] if name == "pikachu" else ["water"],
                "stats": {
                    "hp": 50,
                    "attack": 60,
                    "defense": 50,
                    "special-attack": 70,
                    "special-defense": 60,
                    "speed": 80
                }
            }
        
        pokemon_service.get_pokemon_summary = AsyncMock(side_effect=mock_summary)
        
        result = await pokemon_service.recommend_team_for_battle(
            available_pokemon=["pikachu", "squirtle", "bulbasaur"],
            opponent_types=["fire"],
            team_size=2
        )
        
        assert "recommended_team" in result
        assert len(result["recommended_team"]) == 2
        assert "justification" in result
        assert "team_analysis" in result
        assert result["opponent_types"] == ["fire"]
    
    @pytest.mark.asyncio
    async def test_recommend_team_invalid_team_size(self, pokemon_service):
        """Test team recommendation with invalid team size."""
        with pytest.raises(ValidationError, match="must be between 1 and 6"):
            await pokemon_service.recommend_team_for_battle(
                available_pokemon=["pikachu"],
                team_size=7
            )


class TestGenerationComparison:
    """Test generation comparison utilities."""
    
    @pytest.mark.asyncio
    async def test_compare_generations_by_variety(self, pokemon_service, mock_repository):
        """Test comparing generations by type variety."""
        # Mock generation data
        async def mock_gen(gen_id):
            gens = {
                "1": {
                    "name": "generation-i",
                    "main_region": {"name": "kanto"},
                    "pokemon_species": [
                        {"name": "bulbasaur"},
                        {"name": "charmander"},
                        {"name": "squirtle"}
                    ]
                },
                "2": {
                    "name": "generation-ii",
                    "main_region": {"name": "johto"},
                    "pokemon_species": [
                        {"name": "chikorita"},
                        {"name": "cyndaquil"}
                    ]
                }
            }
            return gens[gen_id]
        
        async def mock_summary(name):
            types_map = {
                "bulbasaur": ["grass", "poison"],
                "charmander": ["fire"],
                "squirtle": ["water"],
                "chikorita": ["grass"],
                "cyndaquil": ["fire"]
            }
            return {
                "name": name,
                "types": types_map.get(name, ["normal"]),
                "stats": {
                    "hp": 50,
                    "attack": 50,
                    "defense": 50,
                    "special-attack": 50,
                    "special-defense": 50,
                    "speed": 50
                }
            }
        
        mock_repository.get_generation = AsyncMock(side_effect=mock_gen)
        pokemon_service.get_pokemon_summary = AsyncMock(side_effect=mock_summary)
        
        result = await pokemon_service.compare_generations(
            generation_ids=["1", "2"],
            criteria="variety"
        )
        
        assert "criteria" in result
        assert result["criteria"] == "variety"
        assert "winner" in result
        assert "comparison_data" in result
        assert "markdown" in result
        assert len(result["generations_compared"]) == 2
        assert "# Generation Comparison" in result["markdown"]
    
    @pytest.mark.asyncio
    async def test_compare_generations_invalid_criteria(self, pokemon_service):
        """Test generation comparison with invalid criteria."""
        with pytest.raises(ValidationError, match="must be one of"):
            await pokemon_service.compare_generations(
                generation_ids=["1"],
                criteria="invalid"
            )
    
    @pytest.mark.asyncio
    async def test_compare_generations_empty_list(self, pokemon_service, mock_repository):
        """Test generation comparison with empty list raises error."""
        # Mock the repository to fail getting generation data
        mock_repository.get_generation = AsyncMock(side_effect=Exception("Not found"))
        
        with pytest.raises(ValidationError, match="No generation data"):
            await pokemon_service.compare_generations(generation_ids=[])


class TestComparePokemons:
    """Test Pokémon comparison utility."""
    
    @pytest.mark.asyncio
    async def test_compare_pokemons_success(self, pokemon_service):
        """Test comparing two Pokémon."""
        async def mock_summary(name):
            summaries = {
                "pikachu": {
                    "name": "pikachu",
                    "types": ["electric"],
                    "stats": {"hp": 35, "attack": 55, "defense": 40}
                },
                "raichu": {
                    "name": "raichu",
                    "types": ["electric"],
                    "stats": {"hp": 60, "attack": 90, "defense": 55}
                }
            }
            return summaries[name]
        
        pokemon_service.get_pokemon_summary = AsyncMock(side_effect=mock_summary)
        
        result = await pokemon_service.compare_pokemons("pikachu", "raichu")
        
        assert "first" in result
        assert "second" in result
        assert "comparison" in result
        assert result["first"]["name"] == "pikachu"
        assert result["second"]["name"] == "raichu"
        assert result["comparison"]["higher_attack"] == "raichu"
        assert result["comparison"]["higher_hp"] == "raichu"
        assert "electric" in result["comparison"]["types_overlap"]
    
    @pytest.mark.asyncio
    async def test_compare_pokemons_empty_names(self, pokemon_service):
        """Test comparing with empty names raises error."""
        with pytest.raises(ValidationError, match="Both pokemon names are required"):
            await pokemon_service.compare_pokemons("", "pikachu")
