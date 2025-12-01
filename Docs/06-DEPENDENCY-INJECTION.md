# Dependency Injection Guide - Best Practices

## Table of Contents
1. [Architecture](#architecture)
2. [SOLID Principles Applied](#solid-principles)
3. [Layer Structure](#layer-structure)
4. [Implemented Patterns](#implemented-patterns)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Extensibility](#extensibility)

---

## Architecture

### Directory Structure
```
backend/
├── core/                    # Application core
│   ├── config.py           # Centralized configuration
│   ├── interfaces.py       # Abstractions/Contracts
│   └── dependencies.py     # DI Container
├── repositories/           # Data layer
│   └── pokemon_repository.py
├── services/              # Business logic
│   └── pokemon_service.py
├── api/                   # Presentation layer
│   └── routes/
│       └── pokemon.py
├── tests/                 # Tests
│   ├── test_pokemon_service.py
│   └── test_api.py
└── main.py               # Entry point
```

---

## SOLID Principles Applied

### 1. **S**ingle Responsibility Principle (SRP)
Each class has a single responsibility:
- `PokeAPIRepository`: Manages external API communication only
- `PokemonService`: Contains business logic only
- `pokemon.py` (routes): Handles HTTP request/response only

### 2. **O**pen/Closed Principle (OCP)
Open for extension, closed for modification:
```python
# New implementations can be created without modifying the service
class DatabasePokemonRepository(IPokemonRepository):
    async def get_pokemon(self, name: str):
        # Database implementation
        pass
```

### 3. **L**iskov Substitution Principle (LSP)
Any implementation of `IPokemonRepository` can substitute another:
```python
# Interchangeable without breaking code
service = PokemonService(PokeAPIRepository(settings))
service = PokemonService(DatabaseRepository(settings))
service = PokemonService(CacheRepository(settings))
```

### 4. **I**nterface Segregation Principle (ISP)
Specific and cohesive interfaces:
```python
# Separated responsibilities
class IPokemonRepository(ABC): ...  # Data only
class IPokemonService(ABC): ...     # Business only
```

### 5. **D**ependency Inversion Principle (DIP)
Depend on abstractions, not implementations:
```python
# ✅ Correct: depends on interface
class PokemonService:
    def __init__(self, repository: IPokemonRepository):
        ...

# ❌ Incorrect: would depend on implementation
class PokemonService:
    def __init__(self, repository: PokeAPIRepository):
        ...
```

---

## Layer Structure

### Dependency Flow
```
HTTP Request
    ↓
API Layer (Routes)
    ↓ [injects]
Service Layer (Business Logic)
    ↓ [injects]
Repository Layer (Data Access)
    ↓
External API / Database
```

### Complete Flow Example
```python
# 1. FastAPI injects Settings
settings = get_settings()

# 2. Settings injected into Repository
repository = PokeAPIRepository(settings)

# 3. Repository injected into Service
service = PokemonService(repository)

# 4. Service injected into handler
@router.get("/{name}")
async def get_pokemon(
    name: str,
    service: IPokemonService = Depends(get_pokemon_service)
):
    return await service.get_pokemon_info(name)
```

---

## Implemented Patterns

### 1. Dependency Injection Pattern
```python
# Constructor Injection (recommended)
class PokemonService:
    def __init__(self, repository: IPokemonRepository):
        self._repository = repository
```

### 2. Repository Pattern
```python
# Abstracts data access
class IPokemonRepository(ABC):
    @abstractmethod
    async def get_pokemon(self, name: str) -> Dict[str, Any]:
        pass
```

### 3. Service Layer Pattern
```python
# Encapsulates business logic
class PokemonService(IPokemonService):
    async def get_pokemon_info(self, name: str):
        # Validations
        # Transformations
        # Orchestration
        pass
```

### 4. Factory Pattern
```python
def create_pokemon_repository(settings: Settings) -> IPokemonRepository:
    return PokeAPIRepository(settings)
```

### 5. Singleton Pattern
```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # Created only once
```

---

## Usage

### 1. Basic Configuration
```python
# .env
DEBUG=true
POKEAPI_TIMEOUT=10.0
```

### 2. Run Application
```bash
uvicorn main:app --reload
```

### 3. Add New Functionality

#### Step 1: Define in Interface
```python
# core/interfaces.py
class IPokemonRepository(ABC):
    @abstractmethod
    async def get_type(self, name: str) -> Dict[str, Any]:
        pass
```

#### Step 2: Implement in Repository
```python
# repositories/pokemon_repository.py
async def get_type(self, name: str) -> Dict[str, Any]:
    return await self._get(f"type/{name.lower()}")
```

#### Step 3: Use in Service
```python
# services/pokemon_service.py
async def get_pokemon_type_info(self, pokemon_name: str):
    pokemon = await self._repository.get_pokemon(pokemon_name)
    types = pokemon.get("types", [])
    # Business logic...
```

#### Step 4: Expose in API
```python
# api/routes/pokemon.py
@router.get("/{name}/types")
async def get_pokemon_types(
    name: str,
    service: IPokemonService = Depends(get_pokemon_service)
):
    return await service.get_pokemon_type_info(name)
```

---

## Testing

### Unit Test (with Mock)
```python
@pytest.fixture
def mock_repository():
    repo = MockPokemonRepository()
    repo.get_pokemon.return_value = {"name": "pikachu", "id": 25}
    return repo

@pytest.fixture
def service(mock_repository):
    # Manual mock injection
    return PokemonService(pokemon_repository=mock_repository)

async def test_get_pokemon(service, mock_repository):
    result = await service.get_pokemon_info("pikachu")
    assert result["name"] == "pikachu"
    mock_repository.get_pokemon.assert_called_once()
```

### Integration Test (Real API)
```python
async def test_integration():
    settings = Settings()
    repository = create_pokemon_repository(settings)
    service = PokemonService(repository)
    
    try:
        result = await service.get_pokemon_info("pikachu")
        assert result["id"] == 25
    finally:
        await repository.close()
```

### Endpoint Test (with Mock)
```python
def test_endpoint(client, mock_service):
    mock_service.get_pokemon_info.return_value = {"name": "pikachu"}
    
    # Override dependency
    app.dependency_overrides[get_pokemon_service] = lambda: mock_service
    
    response = client.get("/pokemon/pikachu")
    assert response.status_code == 200
```

---

## Extensibility

### Alternative Implementation: Cache
```python
class CachedPokemonRepository(IPokemonRepository):
    def __init__(self, base_repository: IPokemonRepository, cache: Cache):
        self._base = base_repository
        self._cache = cache
    
    async def get_pokemon(self, name: str):
        # Search in cache
        cached = await self._cache.get(f"pokemon:{name}")
        if cached:
            return cached
        
        # If not found, get from base repository
        result = await self._base.get_pokemon(name)
        await self._cache.set(f"pokemon:{name}", result, ttl=3600)
        return result
```

### Database Implementation
```python
class DatabasePokemonRepository(IPokemonRepository):
    def __init__(self, db_session: AsyncSession):
        self._db = db_session
    
    async def get_pokemon(self, name: str):
        result = await self._db.execute(
            select(Pokemon).where(Pokemon.name == name)
        )
        return result.scalar_one().to_dict()
```

### Service Composition
```python
class AdvancedPokemonService(IPokemonService):
    def __init__(
        self,
        pokemon_repo: IPokemonRepository,
        analytics_service: IAnalyticsService,
        notification_service: INotificationService
    ):
        self._pokemon_repo = pokemon_repo
        self._analytics = analytics_service
        self._notifications = notification_service
    
    async def get_pokemon_info(self, name: str):
        # Complex logic orchestrating multiple services
        result = await self._pokemon_repo.get_pokemon(name)
        await self._analytics.track("pokemon_viewed", name)
        await self._notifications.notify_admins(f"Pokemon {name} requested")
        return result
```

---

## Architecture Advantages

1. **Testability**: Easy dependency mocking
2. **Maintainability**: Localized changes, low coupling
3. **Scalability**: Add features without breaking existing ones
4. **Clarity**: Each layer has defined responsibilities
5. **Flexibility**: Swap implementations without code changes
6. **Reusability**: Services and repositories are reusable

---

## Useful Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests
pytest tests/test_pokemon_service.py -v

# Run integration tests
pytest tests/ -m integration -v

# Run all tests
pytest tests/ -v

# Coverage
pytest tests/ --cov=. --cov-report=html

# Run application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Best Practices Applied

1. **Constructor injection** (not setters)
2. **Explicit interfaces** (ABC)
3. **Factory functions** for creation
4. **Appropriate dependency scopes** (request vs singleton)
5. **Automatic cleanup** (context managers)
6. **Type hints** everywhere
7. **Externalized configuration** (env vars)
8. **Structured logging** (ready to add)
9. **Error handling** in appropriate layers
10. **Inline documentation** (docstrings)
