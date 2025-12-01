# Pokémon Analysis Utilities - Usage Guide

## Overview

This backend provides advanced Pokémon analysis utilities designed for AI agents and applications. All functions follow best practices with clean architecture, comprehensive testing, and clear documentation.

---

## Quick Start

### 1. Start the API Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. View API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Run Tests

```bash
python -m pytest tests/ -v
```

---

## Core Features

### Data Summarization

All Pokémon data is pre-filtered to include only essential information:

**Included**:
- Basic info (id, name, height, weight)
- Types and abilities
- Stats (HP, Attack, Defense, etc.)
- Sample moves (first 10)
- Sprite URL

**Excluded**:
- Full sprite collections
- Complete move lists (100+ moves)
- Long descriptions
- Redundant metadata

**Benefit**: Reduces data size by ~90%, perfect for LLM context windows.

---

## API Endpoints

### 1. Get Pokémon Summary

```http
GET /pokemon/{name}/summary
```

**Example**:
```bash
curl http://localhost:8000/pokemon/pikachu/summary
```

**Response**:
```json
{
  "id": 25,
  "name": "pikachu",
  "types": ["electric"],
  "abilities": ["static", "lightning-rod"],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special-attack": 50,
    "special-defense": 50,
    "speed": 90
  },
  "height": 4,
  "weight": 60,
  "base_experience": 112
}
```

---

### 2. Group Pokémon by Type

```http
POST /pokemon/group/by-type
```

**Request Body**:
```json
["bulbasaur", "charmander", "squirtle", "pikachu"]
```

**Response**:
```json
{
  "groups": {
    "grass": ["bulbasaur"],
    "fire": ["charmander"],
    "water": ["squirtle"],
    "electric": ["pikachu"]
  },
  "markdown": "# Pokémon Grouped by Primary Type\n\n## Grass Type...",
  "total_pokemons": 4,
  "type_count": 4
}
```

---

### 3. Classify by Battle Role

```http
POST /pokemon/classify/by-role
```

**Roles**:
- **Tank**: High HP (≥200) OR (HP ≥80 AND Defense ≥80)
- **Attacker**: Attack ≥100 OR Special Attack ≥100
- **Fast**: Speed ≥100
- **Balanced**: All others

**Request Body**:
```json
["mewtwo", "blissey", "electrode"]
```

**Response**:
```json
{
  "roles": {
    "attacker": ["mewtwo"],
    "tank": ["blissey"],
    "fast": ["electrode"]
  },
  "markdown": "# Pokémon Classification by Battle Role...",
  "total_classified": 3
}
```

---

### 4. Calculate Team Strength

```http
POST /pokemon/team/strength
```

**Request Body** (max 6 Pokémon):
```json
["pikachu", "charizard", "blastoise"]
```

**Response**:
```json
{
  "team": ["pikachu", "charizard", "blastoise"],
  "team_size": 3,
  "type_coverage": ["electric", "fire", "flying", "water"],
  "average_stats": {
    "hp": 60.33,
    "attack": 70.67,
    "defense": 65.33
  },
  "role_distribution": {
    "attacker": 1,
    "balanced": 2
  },
  "strengths": [
    "Excellent type diversity for coverage",
    "High offensive potential"
  ],
  "recommendations": [
    "Team lacks defensive tanks"
  ],
  "explanation": "## Team Analysis (3 Pokémon)..."
}
```

---

### 5. Recommend Team for Battle

```http
POST /pokemon/team/recommend
```

**Request Body**:
```json
{
  "available_pokemon": ["pikachu", "squirtle", "bulbasaur", "geodude", "onix"],
  "opponent_types": ["fire"],
  "team_size": 3
}
```

**Response**:
```json
{
  "recommended_team": ["squirtle", "geodude", "onix"],
  "opponent_types": ["fire"],
  "justification": "## Recommended Team (3 Pokémon)\n\n**Target**: Counter fire types...",
  "team_analysis": {
    "type_coverage": ["water", "ground", "rock"],
    "strengths": ["Strong type advantage against Fire"]
  }
}
```

---

### 6. Compare Generations

```http
GET /pokemon/generation/compare?generation_ids=1&generation_ids=2&criteria=variety
```

**Criteria Options**:
- `variety`: Type diversity
- `stats`: Average total stats
- `count`: Number of Pokémon

**Response**:
```json
{
  "criteria": "variety",
  "winner": "1",
  "winner_name": "generation-i",
  "winner_score": 15,
  "generations_compared": ["1", "2"],
  "comparison_data": [
    {
      "generation": "1",
      "total_pokemon": 151,
      "type_diversity": 15,
      "average_total_stats": 435.2
    }
  ],
  "markdown": "# Generation Comparison (Criteria: Variety)..."
}
```

---

## Agent Tools (Python)

All utilities are available as Python async functions in `agent/tools.py`:

```python
from agent.tools import (
    get_pokemon_summary,
    group_pokemons_by_type,
    classify_by_role,
    calculate_team_strength,
    recommend_team_for_battle,
    compare_generations
)

# Example: Get summary
summary = await get_pokemon_summary("pikachu")

# Example: Group by type
groups = await group_pokemons_by_type(["bulbasaur", "charmander", "squirtle"])

# Example: Recommend team
team = await recommend_team_for_battle(
    available_pokemon=["pikachu", "charizard", "blastoise"],
    opponent_types=["ground"],
    team_size=3
)
```

---

## Use Case Examples

### Use Case 1: Building a Competitive Team

**User Request**: "Help me build a team to counter Water-type opponents"

**Agent Workflow**:

1. Get available Pokémon (e.g., from user's collection)
2. Call `recommend_team_for_battle()` with `opponent_types=["water"]`
3. Get recommendations prioritizing Grass/Electric types
4. Call `calculate_team_strength()` to analyze the team
5. Present recommendations with justification

**Result**: Optimal team with type advantages and detailed analysis

---

### Use Case 2: Pokémon Organization

**User Request**: "Organize my Pokémon by battle role"

**Agent Workflow**:

1. Get user's Pokémon list
2. Call `classify_by_role()` with the list
3. Receive grouped data (tanks, attackers, fast, balanced)
4. Present Markdown table

**Result**: Clear organization by combat role

---

### Use Case 3: Generation Analysis

**User Request**: "Which generation has the most diverse Pokémon?"

**Agent Workflow**:

1. Call `compare_generations(criteria="variety")`
2. Receive comparison data for Gen 1, 2, 3
3. Get winner and justification
4. Present findings

**Result**: Data-driven answer with explanation

---

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_pokemon_utilities.py -v
```

### Test Coverage

- 41 total tests
- Grouping utilities (3 tests)
- Classification (1 test)
- Team analysis (5 tests)
- Generation comparison (3 tests)
- Integration tests

---

## Architecture

### Dependency Injection

All services receive dependencies via constructor:

```python
class PokemonService:
    def __init__(self, pokemon_repository: IPokemonRepository):
        self._repository = pokemon_repository
```

**Benefits**:
- Easy to test with mocks
- Flexible implementation swapping
- Clear dependencies

---

### Interface-Based Design

```python
class IPokemonRepository(ABC):
    @abstractmethod
    async def get_pokemon(self, name: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_generation(self, name: str) -> Dict[str, Any]:
        pass
```

**Benefits**:
- Multiple implementations (API, cache, mock)
- Testability
- Loose coupling

---

### Caching Support

All repository methods support caching via decorator pattern:

```python
cached_repo = CachedPokemonRepository(
    base_repository=api_repo,
    cache=redis_cache,
    default_ttl=3600
)
```

**Benefits**:
- Reduced API calls
- Faster responses
- Configurable TTL

---

## Performance Considerations

### Limits

- **Generation Comparison**: Analyzes max 50 Pokémon per generation
- **Type Summary**: Returns max 50 Pokémon per type
- **Team Size**: Max 6 Pokémon (standard battle format)

### Optimizations

- Parallel API calls where possible
- Early termination on validation errors
- Efficient data structures (dicts vs lists)
- Caching layer for repeated queries

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid input (e.g., empty list, invalid team size)
- `502`: PokeAPI error (upstream API issue)
- `500`: Internal server error

Example error response:

```json
{
  "detail": "Team size must be between 1 and 6"
}
```

---

## Development

### Project Structure

```
backend/
├── agent/
│   ├── agent.py          # LLM agent implementation
│   └── tools.py          # Agent tools (NEW: 5 utility functions)
├── api/
│   └── routes/
│       └── pokemon.py    # API endpoints (NEW: 5 endpoints)
├── services/
│   └── pokemon_service.py # Business logic (NEW: 5 methods)
├── repositories/
│   └── pokemon_repository.py
├── tests/
│   ├── test_pokemon_utilities.py  # NEW: 13 tests
│   ├── test_pokemon_service.py
│   └── test_api.py
└── main.py
```

### Adding New Utilities

1. **Service Layer** (`services/pokemon_service.py`):
   - Add method with business logic
   - Include error handling and validation
   - Add docstring with examples

2. **API Layer** (`api/routes/pokemon.py`):
   - Create endpoint
   - Add request/response validation
   - Include error handling

3. **Agent Layer** (`agent/tools.py`):
   - Create async wrapper function
   - Add to `TOOLS` dictionary
   - Include docstring

4. **Tests** (`tests/`):
   - Add unit tests
   - Test edge cases
   - Test integration

---

## Examples

Interactive examples are available through:

```bash
# Start API server
uvicorn main:app --reload

# Use the CLI in another terminal
python scripts/pokemon_strategy_cli.py

# Or run quick tests
python scripts/quick_personality_test.py
python scripts/test_agent_comparison.py
```

---

## API Documentation

Full interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Support

For issues or questions:

1. Check the API documentation at `/docs`
2. Review test cases in `tests/test_pokemon_utilities.py`
3. See the scripts in `scripts/` directory
4. Read the comprehensive documentation in `Docs/`

---

## License

[Your License Here]

---

## Changelog

### v2.0.0 - New Utilities Release

**Added**:
- `group_pokemons_by_type()` - Group and visualize by type
- `classify_by_role()` - Classify by battle role
- `calculate_team_strength()` - Analyze team composition
- `recommend_team_for_battle()` - AI-powered team recommendations
- `compare_generations()` - Compare generations by criteria
- 13 comprehensive tests
- Full API documentation
- Usage examples

**Updated**:
- Enhanced `IPokemonRepository` interface
- Updated caching layer for new methods
- Improved error handling across all endpoints

---

**Built with FastAPI, Python, and the PokeAPI**
