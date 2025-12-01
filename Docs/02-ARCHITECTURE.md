# Project Architecture

Documentation describing the complete architecture of the Pokémon Strategy Agent system, its components, and their interactions.

---

## Overview

The project follows a **layered architecture** with **dependency injection** and applies **SOLID** principles.

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ REST API     │  │ CLI Client   │  │ Jupyter NB   │     │
│  │ (FastAPI)    │  │ (Interactive)│  │ (Demos)      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────┐
│         │      AGENT LAYER (AI Reasoning)     │             │
│         │                  │                  │             │
│    ┌────▼──────────────────▼──────────────────▼───┐        │
│    │        Gemini 2.0 Agent with Tools          │        │
│    │  • Strategic Reasoning                       │        │
│    │  • Natural Language Processing               │        │
│    │  • Tool Orchestration                        │        │
│    └────┬──────────────────┬──────────────────┬───┘        │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────┐
│         │     BUSINESS LOGIC LAYER            │             │
│    ┌────▼──────────────────▼──────────────────▼───┐        │
│    │          Pokemon Service                     │        │
│    │  • Team Recommendation                       │        │
│    │  • Classification & Grouping                 │        │
│    │  • Generation Comparison                     │        │
│    │  • Statistical Analysis                      │        │
│    └────┬────────────────────────────────────┬────┘        │
└─────────┼────────────────────────────────────┼──────────────┘
          │                                    │
┌─────────┼────────────────────────────────────┼──────────────┐
│         │       DATA ACCESS LAYER            │              │
│    ┌────▼────────────┐              ┌────────▼────────┐    │
│    │  Repository     │◄─────────────│ Cache Decorator │    │
│    │  (PokeAPI)      │              │ (Redis/Memory)  │    │
│    └────┬────────────┘              └─────────────────┘    │
└─────────┼───────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│               EXTERNAL SERVICES                             │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │  PokeAPI.co  │        │  Google AI   │                  │
│  │  (REST API)  │        │  (Gemini)    │                  │
│  └──────────────┘        └──────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Separation of Concerns (SoC)
Each layer has clearly defined responsibilities:
- **Presentation**: HTTP request/response handling
- **Agent**: AI reasoning and orchestration
- **Business Logic**: Business rules and validation
- **Data Access**: External service communication
- **Infrastructure**: Cache, configuration, utilities

### 2. Dependency Inversion Principle (DIP)
Higher layers depend on abstractions, not concrete implementations:

```python
# ✅ Correct: Service depends on interface
class PokemonService:
    def __init__(self, repository: IPokemonRepository):
        self._repository = repository

# ❌ Incorrect: would depend on concrete implementation
class PokemonService:
    def __init__(self, repository: PokeAPIRepository):
        self._repository = repository
```

### 3. Single Responsibility Principle (SRP)
Each module has a single reason to change:
- `PokeAPIRepository`: Only changes if external API changes
- `PokemonService`: Only changes if business rules change
- `pokemon.py` (routes): Only changes if HTTP contract changes

### 4. Open/Closed Principle (OCP)
Open for extension, closed for modification:

```python
# New repositories can be added without modifying the service
class DatabasePokemonRepository(IPokemonRepository):
    pass

class MockPokemonRepository(IPokemonRepository):
    pass
```

---

## Component Structure

### Core Layer (`core/`)

**Purpose:** Contains abstractions and central configuration.

```
core/
├── interfaces.py          # Contracts (ABCs)
│   ├── IPokemonRepository
│   ├── IPokemonService
│   ├── ICache
│   └── IRateLimiter
├── config.py             # Configuration (Pydantic Settings)
├── dependencies.py       # Dependency Injection Container
├── exceptions.py         # Exception hierarchy
├── cache_interface.py    # Cache interface
└── rate_limit.py        # Rate limiting
```

**Characteristics:**
- No dependencies on other layers
- Defines contracts using ABCs (Abstract Base Classes)
- Centralizes configuration with Pydantic Settings
- Custom exception system

### Agent Layer (`agent/`)

**Purpose:** AI agent implementation with tools.

```
agent/
├── agent.py              # Main agent with Gemini
└── tools.py             # Specialized tools
    ├── recommend_team_for_battle
    ├── classify_pokemons_by_role
    ├── group_pokemons_by_type
    ├── calculate_team_strength
    ├── compare_generations
    └── compare_two_pokemons
```

**Responsibilities:**
- Interpret user intent
- Reason about Pokémon strategy
- Orchestrate tool calls
- Generate natural language explanations

### Service Layer (`services/`)

**Purpose:** Business logic and domain rules.

```
services/
└── pokemon_service.py
    ├── get_pokemon_info()
    ├── search_pokemons()
    ├── get_pokemon_summary()
    ├── get_type_summary()
    ├── compare_pokemons()
    ├── group_pokemons_by_type()
    ├── classify_by_role()
    ├── calculate_team_strength()
    ├── recommend_team_for_battle()
    └── compare_generations()
```

**Responsibilities:**
- Business data validation
- Data transformation and enrichment
- Complex operation orchestration
- Business rule application

### Repository Layer (`repositories/`)

**Purpose:** External data access.

```
repositories/
├── pokemon_repository.py         # PokeAPI implementation
└── cached_pokemon_repository.py  # Cache decorator
```

**Responsibilities:**
- PokeAPI communication
- Network error handling
- Retry logic
- API response transformation

### Infrastructure Layer (`infrastructure/`)

**Purpose:** Infrastructure services.

```
infrastructure/
├── cache_factory.py      # Cache creation factory
├── memory_cache.py       # In-memory implementation
└── redis_cache.py       # Redis implementation
```

**Responsibilities:**
- Concrete cache implementations
- Resource management (connections, pools)
- Infrastructure configuration

### API Layer (`api/`)

**Purpose:** HTTP endpoint exposure.

```
api/
├── pokeapi.py           # Client wrapper
└── routes/
    └── pokemon.py       # REST endpoints
```

**Responsibilities:**
- HTTP request parsing
- Input parameter validation
- HTTP error handling (4xx, 5xx)
- Response serialization
- Rate limiting

---

## Data Flow

### Example: GET /pokemon/{name}

```
1. HTTP Request
   GET /pokemon/pikachu
   
2. FastAPI Router (api/routes/pokemon.py)
   @router.get("/{name}")
   async def get_pokemon(name: str, service: IPokemonService):
       • Validates parameters
       • Applies rate limiting
   
3. Dependency Injection
   service = get_pokemon_service()
   • FastAPI injects PokemonService
   
4. Service Layer (services/pokemon_service.py)
   await service.get_pokemon_info("pikachu")
   • Validates non-empty name
   • Calls repository
   
5. Repository Layer (repositories/pokemon_repository.py)
   await repository.get_pokemon("pikachu")
   
6. Cache Check (cached_pokemon_repository.py)
   • Search in cache
   • If exists → return cached
   • If not exists → continue
   
7. External API Call
   GET https://pokeapi.co/api/v2/pokemon/pikachu
   • Retry logic on failure
   • Timeout handling
   
8. Cache Write
   • Save response in cache
   • TTL = 3600 seconds
   
9. Response Transformation
   • Service enriches data
   • Applies business rules
   
10. HTTP Response
    200 OK
    {
      "id": 25,
      "name": "pikachu",
      "types": ["electric"],
      ...
    }
```

---

## Exception Handling

### Exception Hierarchy

```
PokemonAPIException (base)
├── ValidationError (400)
│   ├── Invalid field
│   ├── Out of range value
│   └── Incorrect format
├── ResourceNotFoundError (404)
│   ├── Pokémon doesn't exist
│   └── Type doesn't exist
├── ExternalAPIError (502)
│   ├── PokeAPI down
│   └── Timeout
├── RateLimitError (429)
│   └── Too many requests
├── CacheError (500)
│   └── Redis unavailable
└── ConfigurationError (500)
    └── Missing environment variable
```

---

## Applied Design Patterns

### 1. Repository Pattern
Abstracts data access:
```python
class IPokemonRepository(ABC):
    @abstractmethod
    async def get_pokemon(self, name: str):
        pass
```

### 2. Service Layer Pattern
Encapsulates business logic:
```python
class PokemonService:
    async def get_pokemon_info(self, name: str):
        # Validations
        # Transformations
        # Business rules
        pass
```

### 3. Dependency Injection
Constructor injection of dependencies:
```python
def __init__(self, repository: IPokemonRepository):
    self._repository = repository
```

### 4. Decorator Pattern
Adds functionality without modifying code:
```python
class CachedPokemonRepository:
    def __init__(self, base_repo, cache):
        self._base = base_repo
        self._cache = cache
```

### 5. Factory Pattern
Complex object creation:
```python
def create_error_wrapper(is_async=False):
    # Returns appropriate wrapper function
    pass
```

---

## Scalability and Performance

### Implemented Strategies

1. **Async/Await Throughout**
   - All I/O operations are asynchronous
   - Non-blocking event loop
   - Multiple concurrent requests

2. **Multi-Level Caching**
   - L1: In-Memory (fast, limited)
   - L2: Redis (shared, persistent)
   - Configurable TTL per data type

3. **Rate Limiting**
   - Prevents PokeAPI overload
   - Protects backend from abuse
   - Configurable per endpoint

4. **Connection Pooling**
   - httpx maintains open connections
   - Reuses TCP connections
   - Reduces latency

5. **Lazy Loading**
   - Loads data only when needed
   - Pagination for large lists
   - Limits on massive analyses

---

## Observability

### Monitoring Points

```python
# 1. Business metrics
- Total requests per endpoint
- Average response time
- Cache hit/miss ratio
- Errors by type

# 2. Infrastructure metrics
- PokeAPI latency
- Memory usage (cache)
- Active connections
- Process CPU and memory

# 3. Structured logs
- Request ID for tracing
- User context
- Stack traces on errors
- Audit logs of critical operations
```

---

## Architectural References

- **Clean Architecture** (Robert C. Martin)
- **Domain-Driven Design** (Eric Evans)
- **Microservices Patterns** (Chris Richardson)
- **API Design Patterns** (JJ Geewax)

---

**Next:** [Project Structure](./03-PROJECT-STRUCTURE.md)
