# Testing Guide

Complete documentation on testing strategies, test execution, and best practices.

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Structure](#test-structure)
3. [Test Types](#test-types)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Fixtures and Mocks](#fixtures-and-mocks)
7. [Coverage](#coverage)
8. [Best Practices](#best-practices)

---

## Testing Philosophy

### Test Pyramid

```
        /\
       /  \
      / UI \         (0 tests - No UI in this project)
     /------\
    /  API  \        (10 tests - HTTP integration tests)
   /----------\
  /  Service  \      (15 tests - Business logic tests)
 /--------------\
/  Unit Tests   \    (16 tests - Pure unit tests)
------------------
```

### Principles

- **Fast:** Quick tests (< 5 seconds total)
- **Independent:** Each test independent
- **Repeatable:** Same results always
- **Self-Validating:** Clear Pass/Fail
- **Timely:** Written alongside code

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures (future)
├── test_api.py                    # HTTP endpoint tests
├── test_cache.py                  # Cache tests
├── test_pokemon_service.py        # Service tests
└── test_pokemon_utilities.py      # Advanced utility tests
```

### Naming Conventions

```python
# Files: test_*.py
test_api.py
test_pokemon_service.py

# Classes: Test*
class TestGroupingUtilities:
    pass

# Functions: test_*
def test_get_pokemon_success():
    pass

# Fixtures: descriptive_name
@pytest.fixture
def pokemon_service():
    pass
```

---

## Test Types

### 1. Unit Tests

**Objective:** Test functions/methods in isolation.

**Characteristics:**
- No external dependencies
- Use of mocks
- Very fast (< 100ms each)

**Example:**
```python
@pytest.mark.asyncio
async def test_get_pokemon_info_empty_name(pokemon_service):
    """Test: error when name is empty."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        await pokemon_service.get_pokemon_info("")
```

### 2. Integration Tests

**Objective:** Test interaction between components.

**Characteristics:**
- May use real API (carefully)
- Verify complete flow
- Slower (< 2s each)

**Example:**
```python
@pytest.mark.asyncio
async def test_integration_get_pokemon():
    """Integration test with real PokeAPI."""
    settings = Settings()
    repository = PokeAPIRepository(settings)
    service = PokemonService(repository)
    
    result = await service.get_pokemon_info("pikachu")
    assert result["id"] == 25
    assert "electric" in [t.get("type", {}).get("name") 
                         for t in result["types"]]
```

### 3. API Tests (HTTP)

**Objective:** Test REST endpoints.

**Characteristics:**
- Use FastAPI TestClient
- Verify status codes and responses
- Simulate real requests

**Example:**
```python
def test_get_pokemon_success(client, mock_service):
    """Test: successful GET /pokemon/{name}."""
    mock_service._get_pokemon_info_mock.return_value = {
        "id": 25,
        "name": "pikachu"
    }
    
    response = client.get("/pokemon/pikachu")
    
    assert response.status_code == 200
    assert response.json()["name"] == "pikachu"
```

### 4. Cache Tests

**Objective:** Verify cache behavior.

**Characteristics:**
- Test TTL
- Verify invalidation
- Test both implementations (Memory/Redis)

**Example:**
```python
@pytest.mark.asyncio
async def test_cache_ttl_expiration():
    """Test: cache entries expire after TTL."""
    cache = InMemoryCache()
    
    await cache.set("key", "value", ttl=1)
    assert await cache.get("key") == "value"
    
    await asyncio.sleep(1.1)
    assert await cache.get("key") is None
```

---

## Running Tests

### Basic Commands

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_pokemon_service.py -v

# Specific test
pytest tests/test_api.py::test_get_pokemon_success -v

# Detailed output
pytest tests/ -vv

# Only tests matching pattern
pytest tests/ -k "pokemon" -v

# Stop on first failure
pytest tests/ -x

# Show prints
pytest tests/ -s

# Quiet mode (errors only)
pytest tests/ -q
```

### Advanced Options

```bash
# Run in parallel (requires pytest-xdist)
pytest tests/ -n auto

# With coverage
pytest tests/ --cov=. --cov-report=html

# Only fast tests (< 1s)
pytest tests/ -m "not slow"

# Rerun only failed tests
pytest tests/ --lf

# Watch mode (reruns on file change)
pytest-watch tests/
```

### Configuration in pytest.ini

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Custom markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

---

## Writing Tests

### AAA Structure (Arrange-Act-Assert)

```python
@pytest.mark.asyncio
async def test_search_pokemons_with_valid_params(pokemon_service, mock_repository):
    # ARRANGE: Prepare data and mocks
    expected_data = {
        "count": 1000,
        "results": [{"name": "bulbasaur"}, {"name": "ivysaur"}]
    }
    mock_repository._list_pokemons_mock.return_value = expected_data
    
    # ACT: Execute function under test
    result = await pokemon_service.search_pokemons(limit=20, offset=0)
    
    # ASSERT: Verify results
    assert result == expected_data
    mock_repository._list_pokemons_mock.assert_called_once()
```

### Exception Testing

```python
@pytest.mark.asyncio
async def test_get_pokemon_info_empty_name(pokemon_service):
    """Test: validation error when name is empty."""
    with pytest.raises(ValidationError) as exc_info:
        await pokemon_service.get_pokemon_info("")
    
    assert "cannot be empty" in str(exc_info.value)
    assert exc_info.value.field == "name"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("limit,expected_error", [
    (0, "must be between"),
    (101, "must be between"),
    (-1, "must be between"),
])
@pytest.mark.asyncio
async def test_search_pokemons_invalid_limit(pokemon_service, limit, expected_error):
    """Test: validation for invalid limits."""
    with pytest.raises(ValidationError, match=expected_error):
        await pokemon_service.search_pokemons(limit=limit)
```

---

## Fixtures and Mocks

### Common Fixtures

```python
# tests/test_pokemon_service.py

@pytest.fixture
def mock_repository():
    """Mock repository with predefined responses."""
    class MockPokemonRepository(IPokemonRepository):
        def __init__(self):
            self._get_pokemon_mock = AsyncMock()
            self._list_pokemons_mock = AsyncMock()
        
        async def get_pokemon(self, name: str):
            return await self._get_pokemon_mock(name)
        
        async def list_pokemons(self, limit: int, offset: int):
            return await self._list_pokemons_mock(limit, offset)
    
    return MockPokemonRepository()

@pytest.fixture
def pokemon_service(mock_repository):
    """PokemonService with mocked repository."""
    return PokemonService(pokemon_repository=mock_repository)
```

### Using Mocks

```python
async def test_get_pokemon(pokemon_service, mock_repository):
    # Configure mock behavior
    mock_repository._get_pokemon_mock.return_value = {
        "id": 25,
        "name": "pikachu"
    }
    
    # Execute
    result = await pokemon_service.get_pokemon_info("pikachu")
    
    # Verify
    assert result["name"] == "pikachu"
    mock_repository._get_pokemon_mock.assert_called_once_with("pikachu")
```

### FastAPI TestClient

```python
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

def test_endpoint(client):
    response = client.get("/pokemon/pikachu")
    assert response.status_code == 200
```

---

## Coverage

### Generate Coverage Report

```bash
# Coverage in terminal
pytest tests/ --cov=services --cov=repositories --cov=agent

# Coverage with HTML report
pytest tests/ --cov=. --cov-report=html

# Open report
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Interpret Coverage

```
Name                    Stmts   Miss  Cover
-------------------------------------------
services/__init__.py        0      0   100%
services/pokemon_service.py   245     12    95%
repositories/__init__.py      0      0   100%
repositories/pokemon_repository.py   108      5    95%
-------------------------------------------
TOTAL                     353     17    95%
```

**Goals:**
- **90%+** - Excellent
- **80-89%** - Acceptable
- **< 80%** - Needs improvement

### Exclude Code from Coverage

```python
def some_function():
    try:
        risky_operation()
    except Exception:  # pragma: no cover
        # This block not counted in coverage
        log_error()
```

---

## Best Practices

### 1. Descriptive Names

```python
# ❌ Bad
def test_1():
    pass

# ✅ Good
def test_get_pokemon_info_returns_correct_data():
    pass
```

### 2. One Assert per Test

```python
# ❌ Bad
def test_pokemon():
    assert result["id"] == 25
    assert result["name"] == "pikachu"
    assert result["types"] == ["electric"]

# ✅ Good
def test_pokemon_id():
    assert result["id"] == 25

def test_pokemon_name():
    assert result["name"] == "pikachu"

def test_pokemon_types():
    assert "electric" in result["types"]
```

### 3. Independence

```python
# ❌ Bad - Tests depend on order
test_data = {}

def test_create():
    test_data["id"] = 1

def test_update():  # Fails if test_create doesn't run first
    assert test_data["id"] == 1

# ✅ Good - Each test independent
@pytest.fixture
def test_data():
    return {"id": 1}

def test_create(test_data):
    assert test_data["id"] == 1

def test_update(test_data):
    assert test_data["id"] == 1
```

### 4. Clean Up Resources

```python
@pytest.fixture
async def cache():
    """Cache with automatic cleanup."""
    cache = InMemoryCache()
    await cache.start_cleanup()
    
    yield cache
    
    # Cleanup
    await cache.close()
```

### 5. Fast Tests

```python
# ❌ Bad - Slow test
def test_with_sleep():
    time.sleep(5)  # Don't do this
    assert True

# ✅ Good - Mock delays
def test_with_mock_sleep(mocker):
    mocker.patch('time.sleep')
    # Test runs instantly
    assert True
```

---

## Debugging Tests

### Verbose Mode

```bash
# See complete output
pytest tests/test_api.py::test_get_pokemon -vv -s

# See locals on failures
pytest tests/ --showlocals

# Full traceback
pytest tests/ --tb=long
```

### PDB (Python Debugger)

```python
def test_something():
    result = function_under_test()
    
    import pdb; pdb.set_trace()  # Breakpoint
    
    assert result == expected
```

**PDB Commands:**
- `n` - Next line
- `s` - Step into
- `c` - Continue
- `p variable` - Print variable
- `l` - List code
- `q` - Quit

### Pytest with PDB

```bash
# Stop on first failure
pytest tests/ --pdb

# Stop on each test
pytest tests/ --trace
```

---

## Project Metrics

### Current Status

```
Total Tests: 41
├── Passing: 41 (100%)
├── Failing: 0
└── Skipped: 0

Coverage: 90%+
├── Services: 95%
├── Repositories: 95%
├── API Routes: 92%
└── Agent: 88%

Execution Time: ~3.5s
├── Unit Tests: ~1.5s
├── Integration: ~2.0s
└── API Tests: ~0.5s
```

### Goals

- Maintain 90%+ coverage
- All tests passing
- Total time < 5s
- Tests for each new feature

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.13
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Additional Resources

- **pytest docs:** https://docs.pytest.org
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/
- **Mock docs:** https://docs.python.org/3/library/unittest.mock.html

---

**Testing is an investment, not a cost. Each test written today saves hours of debugging tomorrow.**
