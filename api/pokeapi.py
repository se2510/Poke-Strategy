"""Robust wrapper for the PokeAPI.

This module provides a `PokeAPI` class that uses a persistent
`requests.Session` with retries and timeouts. For backward
compatibility it also exports top-level functions (e.g. `get_pokemon`)
that call a module-level default client and return an error dict on
failure (matching the previous behavior).
"""

from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import httpx
import asyncio

BASE_URL = "https://pokeapi.co/api/v2"


class PokeAPIError(RuntimeError):
    """Raised when a request to the PokeAPI fails."""


class PokeAPI:
    """Client for the PokeAPI with session, retries and timeouts.

    Methods raise `PokeAPIError` on network/HTTP errors. Use the
    module-level wrapper functions for the older behavior (they return
    error dicts instead of raising).
    """

    def __init__(self, base_url: str = BASE_URL, timeout: float = 5.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/') }"
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", "?")
            text = getattr(e.response, "text", "")
            raise PokeAPIError(f"HTTP {status}: {text}") from e
        except requests.RequestException as e:
            raise PokeAPIError(f"Request failed: {e}") from e

    # -- Basic endpoints (examples). Add more as needed --
    def get_pokemon(self, pokemon_name: str) -> Dict[str, Any]:
        return self._get(f"pokemon/{pokemon_name.lower()}")

    def list_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get("pokemon", params={"limit": limit, "offset": offset})

    def get_ability(self, ability_name: str) -> Dict[str, Any]:
        return self._get(f"ability/{ability_name.lower()}")

    def list_abilities(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get("ability", params={"limit": limit, "offset": offset})

    def get_type(self, type_name: str) -> Dict[str, Any]:
        return self._get(f"type/{type_name.lower()}")

    def list_types(self) -> Dict[str, Any]:
        return self._get("type")

    def get_move(self, move_name: str) -> Dict[str, Any]:
        return self._get(f"move/{move_name.lower()}")

    def list_moves(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get("move", params={"limit": limit, "offset": offset})

    def get_pokemon_species(self, species_name: str) -> Dict[str, Any]:
        return self._get(f"pokemon-species/{species_name.lower()}")

    def get_evolution_chain(self, chain_id: int) -> Dict[str, Any]:
        return self._get(f"evolution-chain/{chain_id}")

    def get_location(self, location_name: str) -> Dict[str, Any]:
        return self._get(f"location/{location_name.lower()}")

    def list_locations(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get("location", params={"limit": limit, "offset": offset})

    def get_item(self, item_name: str) -> Dict[str, Any]:
        return self._get(f"item/{item_name.lower()}")

    def list_items(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get("item", params={"limit": limit, "offset": offset})

    def get_type_chart(self) -> Dict[str, Any]:
        types = self.list_types().get("results", [])
        chart: Dict[str, Any] = {}
        for t in types:
            td = self.get_type(t["name"]) if isinstance(t, dict) and "name" in t else {}
            chart[t.get("name", str(t))] = td.get("damage_relations", {}) if isinstance(td, dict) else {}
        return chart

    def get_generation(self, generation_name: str) -> Dict[str, Any]:
        return self._get(f"generation/{generation_name.lower()}")

    def list_generations(self) -> Dict[str, Any]:
        return self._get("generation")

    def get_game_version(self, version_name: str) -> Dict[str, Any]:
        return self._get(f"version/{version_name.lower()}")

    def list_game_versions(self) -> Dict[str, Any]:
        return self._get("version")

    def get_stat(self, stat_name: str) -> Dict[str, Any]:
        return self._get(f"stat/{stat_name.lower()}")

    def list_stats(self) -> Dict[str, Any]:
        return self._get("stat")

    def get_nature(self, nature_name: str) -> Dict[str, Any]:
        return self._get(f"nature/{nature_name.lower()}")

    def list_natures(self) -> Dict[str, Any]:
        return self._get("nature")

    def get_growth_rate(self, growth_rate_name: str) -> Dict[str, Any]:
        return self._get(f"growth-rate/{growth_rate_name.lower()}")

    def list_growth_rates(self) -> Dict[str, Any]:
        return self._get("growth-rate")

    def get_habitats(self) -> Dict[str, Any]:
        return self._get("pokemon-habitat")

    def get_habitat(self, habitat_name: str) -> Dict[str, Any]:
        return self._get(f"pokemon-habitat/{habitat_name.lower()}")

    def get_shape(self, shape_name: str) -> Dict[str, Any]:
        return self._get(f"pokemon-shape/{shape_name.lower()}")

    def list_shapes(self) -> Dict[str, Any]:
        return self._get("pokemon-shape")

    def get_color(self, color_name: str) -> Dict[str, Any]:
        return self._get(f"pokemon-color/{color_name.lower()}")

    def list_colors(self) -> Dict[str, Any]:
        return self._get("pokemon-color")

    def get_egg_group(self, egg_group_name: str) -> Dict[str, Any]:
        return self._get(f"egg-group/{egg_group_name.lower()}")

    def list_egg_groups(self) -> Dict[str, Any]:
        return self._get("egg-group")

    def get_contest_type(self, contest_type_name: str) -> Dict[str, Any]:
        return self._get(f"contest-type/{contest_type_name.lower()}")

    def list_contest_types(self) -> Dict[str, Any]:
        return self._get("contest-type")

    def get_contest_effect(self, effect_id: int) -> Dict[str, Any]:
        return self._get(f"contest-effect/{effect_id}")

    def get_super_contest_effect(self, effect_id: int) -> Dict[str, Any]:
        return self._get(f"super-contest-effect/{effect_id}")


# Module-level default client for convenience / backward compatibility
default_client = PokeAPI()


# --- Generic wrapper factory to eliminate duplication ---
from typing import Callable, TypeVar, Awaitable

T = TypeVar('T')


def create_error_wrapper(is_async: bool = False) -> Callable:
    """Factory to create sync or async error wrapper functions.
    
    Args:
        is_async: If True, creates async wrapper; otherwise sync wrapper
        
    Returns:
        Wrapper function that catches PokeAPIError and returns error dict
    """
    if is_async:
        async def async_wrapper(fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T | Dict[str, str]:
            try:
                return await fn(*args, **kwargs)
            except PokeAPIError as e:
                return {"error": str(e)}
        return async_wrapper
    else:
        def sync_wrapper(fn: Callable[..., T], *args, **kwargs) -> T | Dict[str, str]:
            try:
                return fn(*args, **kwargs)
            except PokeAPIError as e:
                return {"error": str(e)}
        return sync_wrapper


# Create wrappers using factory
_wrap = create_error_wrapper(is_async=False)
_async_wrap = create_error_wrapper(is_async=True)


def get_pokemon(pokemon_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_pokemon, pokemon_name)


def list_pokemons(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return _wrap(default_client.list_pokemons, limit, offset)


def get_ability(ability_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_ability, ability_name)


def list_abilities(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return _wrap(default_client.list_abilities, limit, offset)


def get_type(type_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_type, type_name)


def list_types() -> Dict[str, Any]:
    return _wrap(default_client.list_types)


def get_move(move_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_move, move_name)


def list_moves(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return _wrap(default_client.list_moves, limit, offset)


def get_pokemon_species(species_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_pokemon_species, species_name)


def get_evolution_chain(chain_id: int) -> Dict[str, Any]:
    return _wrap(default_client.get_evolution_chain, chain_id)


def get_location(location_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_location, location_name)


def list_locations(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return _wrap(default_client.list_locations, limit, offset)


def get_item(item_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_item, item_name)


def list_items(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return _wrap(default_client.list_items, limit, offset)


def get_type_chart() -> Dict[str, Any]:
    return _wrap(default_client.get_type_chart)


def get_generation(generation_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_generation, generation_name)


def list_generations() -> Dict[str, Any]:
    return _wrap(default_client.list_generations)


def get_game_version(version_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_game_version, version_name)


def list_game_versions() -> Dict[str, Any]:
    return _wrap(default_client.list_game_versions)


def get_stat(stat_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_stat, stat_name)


def list_stats() -> Dict[str, Any]:
    return _wrap(default_client.list_stats)


def get_nature(nature_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_nature, nature_name)


def list_natures() -> Dict[str, Any]:
    return _wrap(default_client.list_natures)


def get_growth_rate(growth_rate_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_growth_rate, growth_rate_name)


def list_growth_rates() -> Dict[str, Any]:
    return _wrap(default_client.list_growth_rates)


def get_habitats() -> Dict[str, Any]:
    return _wrap(default_client.get_habitats)


def get_habitat(habitat_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_habitat, habitat_name)


def get_shape(shape_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_shape, shape_name)


def list_shapes() -> Dict[str, Any]:
    return _wrap(default_client.list_shapes)


def get_color(color_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_color, color_name)


def list_colors() -> Dict[str, Any]:
    return _wrap(default_client.list_colors)


def get_egg_group(egg_group_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_egg_group, egg_group_name)


def list_egg_groups() -> Dict[str, Any]:
    return _wrap(default_client.list_egg_groups)


def get_contest_type(contest_type_name: str) -> Dict[str, Any]:
    return _wrap(default_client.get_contest_type, contest_type_name)


def list_contest_types() -> Dict[str, Any]:
    return _wrap(default_client.list_contest_types)


def get_contest_effect(effect_id: int) -> Dict[str, Any]:
    return _wrap(default_client.get_contest_effect, effect_id)


def get_super_contest_effect(effect_id: int) -> Dict[str, Any]:
    return _wrap(default_client.get_super_contest_effect, effect_id)


# --- Async client and async wrappers ---
class AsyncPokeAPI:
    """Async client for the PokeAPI using `httpx.AsyncClient`.

    The async client implements simple manual retries with exponential
    backoff for idempotent GET requests.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: float = 5.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        backoff = 0.3
        for attempt in range(self.max_retries):
            try:
                resp = await self._client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code if e.response is not None else None
                # retry on transient server errors / rate limit
                if status in (429, 500, 502, 503, 504) and attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                text = e.response.text if e.response is not None else ""
                raise PokeAPIError(f"HTTP {status}: {text}") from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise PokeAPIError(f"Request failed: {e}") from e

    # Async endpoint methods
    async def get_pokemon(self, pokemon_name: str) -> Dict[str, Any]:
        return await self._get(f"pokemon/{pokemon_name.lower()}")

    async def list_pokemons(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._get("pokemon", params={"limit": limit, "offset": offset})

    async def get_ability(self, ability_name: str) -> Dict[str, Any]:
        return await self._get(f"ability/{ability_name.lower()}")

    async def list_abilities(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._get("ability", params={"limit": limit, "offset": offset})

    async def get_type(self, type_name: str) -> Dict[str, Any]:
        return await self._get(f"type/{type_name.lower()}")

    async def list_types(self) -> Dict[str, Any]:
        return await self._get("type")

    async def get_move(self, move_name: str) -> Dict[str, Any]:
        return await self._get(f"move/{move_name.lower()}")

    async def list_moves(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._get("move", params={"limit": limit, "offset": offset})

    async def get_pokemon_species(self, species_name: str) -> Dict[str, Any]:
        return await self._get(f"pokemon-species/{species_name.lower()}")

    async def get_evolution_chain(self, chain_id: int) -> Dict[str, Any]:
        return await self._get(f"evolution-chain/{chain_id}")

    async def get_location(self, location_name: str) -> Dict[str, Any]:
        return await self._get(f"location/{location_name.lower()}")

    async def list_locations(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._get("location", params={"limit": limit, "offset": offset})

    async def get_item(self, item_name: str) -> Dict[str, Any]:
        return await self._get(f"item/{item_name.lower()}")

    async def list_items(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._get("item", params={"limit": limit, "offset": offset})

    async def get_type_chart(self) -> Dict[str, Any]:
        types = (await self.list_types()).get("results", [])
        chart: Dict[str, Any] = {}
        for t in types:
            name = t.get("name") if isinstance(t, dict) else None
            td = await self.get_type(name) if name else {}
            chart[name or str(t)] = td.get("damage_relations", {}) if isinstance(td, dict) else {}
        return chart

    async def get_generation(self, generation_name: str) -> Dict[str, Any]:
        return await self._get(f"generation/{generation_name.lower()}")

    async def list_generations(self) -> Dict[str, Any]:
        return await self._get("generation")

    async def get_game_version(self, version_name: str) -> Dict[str, Any]:
        return await self._get(f"version/{version_name.lower()}")

    async def list_game_versions(self) -> Dict[str, Any]:
        return await self._get("version")

    async def get_stat(self, stat_name: str) -> Dict[str, Any]:
        return await self._get(f"stat/{stat_name.lower()}")

    async def list_stats(self) -> Dict[str, Any]:
        return await self._get("stat")

    async def get_nature(self, nature_name: str) -> Dict[str, Any]:
        return await self._get(f"nature/{nature_name.lower()}")

    async def list_natures(self) -> Dict[str, Any]:
        return await self._get("nature")

    async def get_growth_rate(self, growth_rate_name: str) -> Dict[str, Any]:
        return await self._get(f"growth-rate/{growth_rate_name.lower()}")

    async def list_growth_rates(self) -> Dict[str, Any]:
        return await self._get("growth-rate")

    async def get_habitats(self) -> Dict[str, Any]:
        return await self._get("pokemon-habitat")

    async def get_habitat(self, habitat_name: str) -> Dict[str, Any]:
        return await self._get(f"pokemon-habitat/{habitat_name.lower()}")

    async def get_shape(self, shape_name: str) -> Dict[str, Any]:
        return await self._get(f"pokemon-shape/{shape_name.lower()}")

    async def list_shapes(self) -> Dict[str, Any]:
        return await self._get("pokemon-shape")

    async def get_color(self, color_name: str) -> Dict[str, Any]:
        return await self._get(f"pokemon-color/{color_name.lower()}")

    async def list_colors(self) -> Dict[str, Any]:
        return await self._get("pokemon-color")

    async def get_egg_group(self, egg_group_name: str) -> Dict[str, Any]:
        return await self._get(f"egg-group/{egg_group_name.lower()}")

    async def list_egg_groups(self) -> Dict[str, Any]:
        return await self._get("egg-group")

    async def get_contest_type(self, contest_type_name: str) -> Dict[str, Any]:
        return await self._get(f"contest-type/{contest_type_name.lower()}")

    async def list_contest_types(self) -> Dict[str, Any]:
        return await self._get("contest-type")

    async def get_contest_effect(self, effect_id: int) -> Dict[str, Any]:
        return await self._get(f"contest-effect/{effect_id}")

    async def get_super_contest_effect(self, effect_id: int) -> Dict[str, Any]:
        return await self._get(f"super-contest-effect/{effect_id}")


# Module-level default async client
default_async_client = AsyncPokeAPI()


async def async_get_pokemon(pokemon_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_pokemon, pokemon_name)


async def async_list_pokemons(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_pokemons, limit, offset)


async def async_get_ability(ability_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_ability, ability_name)


async def async_list_abilities(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_abilities, limit, offset)


async def async_get_type(type_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_type, type_name)


async def async_list_types() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_types)


async def async_get_move(move_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_move, move_name)


async def async_list_moves(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_moves, limit, offset)


async def async_get_pokemon_species(species_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_pokemon_species, species_name)


async def async_get_evolution_chain(chain_id: int) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_evolution_chain, chain_id)


async def async_get_location(location_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_location, location_name)


async def async_list_locations(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_locations, limit, offset)


async def async_get_item(item_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_item, item_name)


async def async_list_items(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_items, limit, offset)


async def async_get_type_chart() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_type_chart)


async def async_get_generation(generation_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_generation, generation_name)


async def async_list_generations() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_generations)


async def async_get_game_version(version_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_game_version, version_name)


async def async_list_game_versions() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_game_versions)


async def async_get_stat(stat_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_stat, stat_name)


async def async_list_stats() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_stats)


async def async_get_nature(nature_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_nature, nature_name)


async def async_list_natures() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_natures)


async def async_get_growth_rate(growth_rate_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_growth_rate, growth_rate_name)


async def async_list_growth_rates() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_growth_rates)


async def async_get_habitats() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_habitats)


async def async_get_habitat(habitat_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_habitat, habitat_name)


async def async_get_shape(shape_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_shape, shape_name)


async def async_list_shapes() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_shapes)


async def async_get_color(color_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_color, color_name)


async def async_list_colors() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_colors)


async def async_get_egg_group(egg_group_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_egg_group, egg_group_name)


async def async_list_egg_groups() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_egg_groups)


async def async_get_contest_type(contest_type_name: str) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_contest_type, contest_type_name)


async def async_list_contest_types() -> Dict[str, Any]:
    return await _async_wrap(default_async_client.list_contest_types)


async def async_get_contest_effect(effect_id: int) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_contest_effect, effect_id)


async def async_get_super_contest_effect(effect_id: int) -> Dict[str, Any]:
    return await _async_wrap(default_async_client.get_super_contest_effect, effect_id)

