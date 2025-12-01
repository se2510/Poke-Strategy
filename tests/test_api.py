"""Integration tests for API endpoints with dependency overrides."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from main import app
from core.dependencies import get_pokemon_service
from core.interfaces import IPokemonService


class MockPokemonService(IPokemonService):
    """Mock del servicio para testing de API."""
    
    def __init__(self):
        self._get_pokemon_info_mock = AsyncMock()
        self._search_pokemons_mock = AsyncMock()
        self._get_pokemon_summary_mock = AsyncMock()
        self._get_type_summary_mock = AsyncMock()
        self._compare_pokemons_mock = AsyncMock()
    
    async def get_pokemon_info(self, name: str):
        return await self._get_pokemon_info_mock(name)
    
    async def search_pokemons(self, limit: int = 20, offset: int = 0):
        return await self._search_pokemons_mock(limit=limit, offset=offset)
    async def get_pokemon_summary(self, name: str):
        return await self._get_pokemon_summary_mock(name)
    async def get_type_summary(self, type_name: str, limit: int = 10):
        return await self._get_type_summary_mock(type_name, limit)
    async def compare_pokemons(self, first: str, second: str):
        result = await self._compare_pokemons_mock(first, second)
        # Ensure dict is returned (avoid leaking AsyncMock)
        return dict(result)


@pytest.fixture
def mock_service():
    """Fixture que proporciona un servicio mock."""
    return MockPokemonService()


@pytest.fixture
def client(mock_service):
    """Fixture que proporciona un cliente de prueba con servicio mock.
    
    Sobrescribe la dependencia get_pokemon_service para que use el mock.
    """
    app.dependency_overrides[get_pokemon_service] = lambda: mock_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_pokemon_success(client, mock_service):
    """Test: endpoint GET /pokemon/{name} exitoso."""
    # Arrange
    mock_service._get_pokemon_info_mock.return_value = {
        "name": "pikachu",
        "id": 25
    }
    
    # Act
    response = client.get("/pokemon/pikachu")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "pikachu"
    mock_service._get_pokemon_info_mock.assert_called_once()


def test_get_pokemon_invalid_name(client, mock_service):
    """Test: endpoint retorna 400 cuando el nombre es inválido."""
    # Arrange
    from core.exceptions import ValidationError
    mock_service._get_pokemon_info_mock.side_effect = ValidationError(
        message="nombre inválido",
        field="name",
        value="invalid-pokemon-name"
    )
    
    # Act
    response = client.get("/pokemon/invalid-pokemon-name")
    
    # Assert
    assert response.status_code == 400
    assert "nombre inválido" in str(response.json()["detail"])


def test_list_pokemons_success(client, mock_service):
    """Test: endpoint GET /pokemon/ exitoso."""
    # Arrange
    mock_service._search_pokemons_mock.return_value = {
        "count": 2,
        "results": [{"name": "bulbasaur"}, {"name": "ivysaur"}]
    }
    
    # Act
    response = client.get("/pokemon/?limit=2&offset=0")
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()["results"]) == 2


def test_get_pokemon_summary_success(client, mock_service):
    mock_service._get_pokemon_summary_mock.return_value = {
        "id": 25,
        "name": "pikachu",
        "types": ["electric"],
        "abilities": ["static"],
        "stats": {"attack": 55},
        "moves_sample": ["thunderbolt"],
        "moves_count": 1
    }
    response = client.get("/pokemon/pikachu/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    assert "moves" not in data
    assert "moves_sample" in data


def test_get_type_summary_success(client, mock_service):
    mock_service._get_type_summary_mock.return_value = {
        "type": "electric",
        "total_available": 2,
        "returned": 2,
        "pokemons": [
            {"name": "pikachu", "id": 25},
            {"name": "raichu", "id": 26},
        ]
    }
    response = client.get("/pokemon/type/electric/summary?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "electric"
    assert data["returned"] == 2


def test_compare_pokemons_success(client, mock_service):
    mock_service._compare_pokemons_mock.return_value = {
        "first": {"name": "pikachu", "stats": {"attack": 55}},
        "second": {"name": "bulbasaur", "stats": {"attack": 49}},
        "comparison": {"higher_attack": "pikachu"}
    }
    response = client.get("/pokemon/compare?first=pikachu&second=bulbasaur")
    assert response.status_code == 200
    data = response.json()
    assert data["comparison"]["higher_attack"] == "pikachu"


def test_cache_stats_endpoint(client):
    response = client.get("/pokemon/cache/stats")
    assert response.status_code == 200
    assert "hits" in response.json()


def test_rate_status_endpoint(client):
    response = client.get("/pokemon/rate/status")
    assert response.status_code == 200
    body = response.json()
    assert "remaining" in body


def test_health_endpoint(client):
    """Test: endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test: endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    assert "app" in response.json()
