# Project Structure

Complete documentation of the project's directory and file organization.

## Directory Tree

```
backend/
├── agent/                         # AI Agent and tools
│   ├── __init__.py
│   ├── agent.py                   # Main agent with Gemini
│   └── tools.py                   # Agent tools
│
├── api/                           # API layer
│   ├── pokeapi.py                 # PokeAPI wrapper client
│   └── routes/
│       ├── __init__.py
│       └── pokemon.py             # REST endpoints
│
├── core/                          # System core
│   ├── __init__.py
│   ├── cache_interface.py         # Cache interface
│   ├── config.py                  # Configuration (Pydantic Settings)
│   ├── dependencies.py            # DI container
│   ├── exceptions.py              # Exception system
│   ├── interfaces.py              # Contracts (ABCs)
│   └── rate_limit.py             # Rate limiting
│
├── infrastructure/                # Infrastructure services
│   ├── __init__.py
│   ├── cache_factory.py           # Cache factory
│   ├── memory_cache.py            # In-memory cache
│   └── redis_cache.py             # Redis cache
│
├── repositories/                  # Data access layer
│   ├── __init__.py
│   ├── pokemon_repository.py      # PokeAPI repository
│   └── cached_pokemon_repository.py  # Cache decorator
│
├── services/                      # Business logic
│   ├── __init__.py
│   └── pokemon_service.py         # Pokemon service
│
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_api.py                # Endpoint tests
│   ├── test_cache.py              # Cache tests
│   ├── test_pokemon_service.py    # Service tests
│   └── test_pokemon_utilities.py  # Utility tests
│
├── Docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── 01-QUICK-START.md          # Quick start guide
│   ├── 02-ARCHITECTURE.md         # System architecture
│   ├── 03-PROJECT-STRUCTURE.md    # This file
│   └── ...                        # Additional documents
│
├── scripts/                       # Utility scripts
│   ├── pokemon_strategy_cli.py    # Interactive CLI
│   ├── quick_personality_test.py  # Quick personality test
│   ├── test_agent_comparison.py   # Agent comparison
│   └── README.md                  # Scripts documentation
│
├── main.py                        # FastAPI entry point
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── .env.example                   # Environment variables template
├── .env                           # Environment variables (not in git)
│
└── README.md                      # Main project README
```

## Module Descriptions

### `agent/` - AI Agent

#### `agent.py`
**Purpose:** Google Gemini agent implementation.

**Contents:**
- Gemini 2.0 model configuration
- Available tools definition
- Prompt generation
- Conversation handling

**Main classes:**
```python
class PokemonStrategyAgent:
    def __init__(self, api_key: str, base_url: str)
    async def ask(self, question: str) -> str
    async def _execute_tool(self, tool_name: str, params: dict)
```

#### `tools.py`
**Purpose:** Specialized agent tools.

**Functions:**
- `recommend_team_for_battle()` - Recommends optimal team
- `classify_pokemons_by_role()` - Classifies by combat role
- `group_pokemons_by_type()` - Groups by type
- `calculate_team_strength()` - Analyzes strengths
- `compare_generations()` - Compares generations
- `compare_two_pokemons()` - Compares two Pokemon

### `api/` - API Layer

#### `pokeapi.py`
**Purpose:** PokeAPI wrapper client.

**Functions:**
- Synchronous and asynchronous functions
- Retry logic with exponential backoff
- Robust error handling
- Factory for creating wrappers

**Example:**
```python
def get_pokemon(name: str) -> dict:
    """Retrieves Pokemon data (synchronous)."""
    
async def get_pokemon_async(name: str) -> dict:
    """Retrieves Pokemon data (asynchronous)."""
```

#### `routes/pokemon.py`
**Purpose:** REST endpoint definitions.

**Main endpoints:**
- `GET /pokemon/{name}` - Get Pokemon
- `GET /pokemon/` - List Pokemon
- `GET /pokemon/{name}/summary` - Compact summary
- `POST /pokemon/team/recommend` - Recommend team
- `POST /pokemon/group/by-type` - Group by type
- `POST /pokemon/classify/by-role` - Classify by role
- `GET /pokemon/generation/compare` - Compare generations

**Features:**
- Pydantic validation
- Rate limiting
- Exception handling with decorator
- Automatic documentation (OpenAPI)

### `core/` - System Core

#### `interfaces.py`
**Purpose:** Contract definitions using ABCs.

**Interfaces:**
```python
class IPokemonRepository(ABC):
    """Contract for Pokemon repositories."""
    
class IPokemonService(ABC):
    """Contract for business services."""
    
class ICache(ABC):
    """Contract for cache implementations."""
```

#### `config.py`
**Purpose:** Centralized configuration with Pydantic Settings.

**Configurations:**
- PokeAPI (URL, timeout)
- Cache (type, TTL)
- Rate limiting
- Google API Key
- Debug mode

```python
class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"
    CACHE_ENABLED: bool = True
    CACHE_TYPE: str = "memory"
    CACHE_TTL: int = 3600
```

#### `dependencies.py`
**Purpose:** Dependency injection container.

**Factory functions:**
- `get_settings()` - Configuration singleton
- `get_cache()` - Cache factory
- `get_pokemon_repository()` - Repository factory
- `get_pokemon_service()` - Service factory

#### `exceptions.py`
**Purpose:** Custom exception hierarchy.

**Classes:**
- `PokemonAPIException` - Base class
- `ValidationError` - Validation errors (400)
- `ResourceNotFoundError` - Resource not found (404)
- `ExternalAPIError` - External API error (502)
- `RateLimitError` - Rate limit exceeded (429)
- `CacheError` - Cache error (500)
- `ConfigurationError` - Configuration error (500)

### `infrastructure/` - Infrastructure

#### `cache_factory.py`
**Purpose:** Cache instance creation factory.

```python
def create_cache(cache_type: str, **kwargs) -> ICache:
    if cache_type == "memory":
        return InMemoryCache()
    elif cache_type == "redis":
        return RedisCache(**kwargs)
```

#### `memory_cache.py`
**Purpose:** In-memory cache implementation.

**Features:**
- TTL per entry
- Automatic cleanup of expired entries
- Thread-safe
- No external dependencies

#### `redis_cache.py`
**Purpose:** Redis cache implementation.

**Features:**
- TTL support
- Optional persistence
- Shared across workers
- JSON serialization

### `repositories/` - Data Access

#### `pokemon_repository.py`
**Purpose:** PokeAPI repository implementation.

**Methods:**
- `get_pokemon(name)` - Get Pokemon by name
- `list_pokemons(limit, offset)` - List with pagination
- `get_type(name)` - Get type information
- `get_ability(name)` - Get ability
- `get_generation(id)` - Get generation

**Features:**
- Asynchronous operations
- Retry logic
- Timeout handling
- Error transformation

#### `cached_pokemon_repository.py`
**Purpose:** Decorator adding cache to base repository.

**Pattern:**
```python
class CachedPokemonRepository(IPokemonRepository):
    def __init__(self, base_repository, cache):
        self._base = base_repository
        self._cache = cache
    
    async def get_pokemon(self, name):
        # Check cache
        cached = await self._cache.get(f"pokemon:{name}")
        if cached:
            return cached
        
        # Get from base repository
        result = await self._base.get_pokemon(name)
        
        # Store in cache
        await self._cache.set(f"pokemon:{name}", result, ttl=3600)
        return result
```

### `services/` - Business Logic

#### `pokemon_service.py`
**Purpose:** Business logic implementation.

**Main methods:**

**Basic queries:**
- `get_pokemon_info(name)` - Complete information
- `search_pokemons(limit, offset)` - Paginated search
- `get_pokemon_summary(name)` - Compact summary

**Analysis:**
- `get_type_summary(type_name, limit)` - Type summary
- `compare_pokemons(first, second)` - Comparison

**Advanced utilities:**
- `group_pokemons_by_type(names)` - Grouping
- `classify_by_role(names)` - Classification
- `calculate_team_strength(names)` - Team analysis
- `recommend_team_for_battle(available, opponents, size)` - Recommendation
- `compare_generations(ids, criteria)` - Generation comparison

**Validations:**
- Non-empty names
- Valid ranges (limit, offset)
- Team size (1-6)
- Valid criteria

### `tests/` - Tests

#### Test Structure

```python
# test_api.py
- HTTP endpoint tests
- FastAPI TestClient integration
- Service mocks

# test_cache.py
- In-memory cache tests
- Redis cache tests
- Decorator tests

# test_pokemon_service.py
- Service unit tests
- Repository mocks
- Business validations

# test_pokemon_utilities.py
- Advanced utility tests
- Classification and grouping
- Recommendations
```

**Common fixtures:**
```python
@pytest.fixture
def mock_repository():
    """Repository mock."""
    
@pytest.fixture
def pokemon_service(mock_repository):
    """Service with mocked repository."""
    
@pytest.fixture
def client(mock_service):
    """FastAPI test client."""
```

### `Docs/` - Documentation

Complete documentation structure:
- User guides (Quick Start, CLI, Notebooks)
- Technical documentation (Architecture, API)
- Development guides (Testing, Standards)
- Deployment and operations

## Configuration Files

### `requirements.txt`
**Main dependencies:**
```
fastapi>=0.118.3
uvicorn>=0.32.1
httpx>=0.27.2
pydantic>=2.0.0
pydantic-settings>=2.0.0
google-generativeai>=0.8.3
pytest>=8.3.4
pytest-asyncio>=0.25.2
```

### `pytest.ini`
**Pytest configuration:**
```ini
[pytest]
pythonpath = .
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### `.env.example`
**Environment variables template:**
```env
# Google AI (Required)
GOOGLE_API_KEY=your-api-key-here

# PokeAPI Configuration
POKEAPI_BASE_URL=https://pokeapi.co/api/v2
POKEAPI_TIMEOUT=10.0

# Cache Configuration
CACHE_ENABLED=true
CACHE_TYPE=memory
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Application
DEBUG=true
```

## Code Conventions

### File Names
- **Modules:** `snake_case.py`
- **Tests:** `test_*.py`
- **Notebooks:** `descriptive_name.ipynb`

### Class Names
```python
# Interfaces: 'I' prefix
class IPokemonRepository(ABC): pass

# Implementations: descriptive name
class PokeAPIRepository(IPokemonRepository): pass

# Services: 'Service' suffix
class PokemonService: pass

# Exceptions: 'Error' suffix
class ValidationError(PokemonAPIException): pass
```

### Function Names
```python
# Public functions: snake_case
async def get_pokemon_info(name: str): pass

# Private functions: '_' prefix
async def _get(self, endpoint: str): pass

# Factory functions: 'create_' or 'get_' prefix
def create_cache(): pass
def get_settings(): pass
```

## Project Metrics

```
Lines of Code:
├── agent/          ~500 lines
├── api/            ~400 lines
├── core/           ~300 lines
├── repositories/   ~350 lines
├── services/       ~800 lines
├── tests/          ~600 lines
└── Total:          ~3000 lines

Files:
├── Python:         25 files
├── Tests:          4 files
├── Docs:           20+ files
└── Config:         3 files

Test Coverage:
├── Unit Tests:     35 tests
├── Integration:    6 tests
├── Coverage:       >90%
└── Total:          41 tests
```

## Next Steps

To understand component interactions:
1. Review [Project Architecture](./02-ARCHITECTURE.md)
2. Consult [API Guide](./04-API-REFERENCE.md)
3. Explore [Use Cases](./13-USE-CASES.md)

Project organized following software architecture best practices.
