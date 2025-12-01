"""Pokemon API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from typing import Dict, Any, List

from core.interfaces import IPokemonService
from core.dependencies import get_pokemon_service
from core.exceptions import (
    ExternalAPIError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError
)
from core.dependencies import get_cache
from core.cache_interface import ICache
from core.rate_limit import rate_limit, rate_status


def handle_exceptions(func):
    """Decorator to handle exceptions consistently across all endpoints."""
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RateLimitError as e:
            raise HTTPException(status_code=e.status_code or 429, detail=e.to_dict())
        except ValidationError as e:
            raise HTTPException(status_code=e.status_code or 400, detail=e.to_dict())
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=e.status_code or 404, detail=e.to_dict())
        except ExternalAPIError as e:
            raise HTTPException(status_code=e.status_code or 502, detail=e.to_dict())
        except Exception as e:
            raise HTTPException(status_code=500, detail={"error": "InternalError", "message": str(e)})
    
    return wrapper


router = APIRouter(
    prefix="/pokemon",
    tags=["pokemon"],
)




@router.get("/")
async def list_pokemons(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100, description="Number of results"),
    offset: int = Query(default=0, ge=0, description="Starting index"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """List pokemons with pagination."""
    try:
        rate_limit(request)
        result = await service.search_pokemons(limit=limit, offset=offset)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=e.status_code or 400, detail=e.to_dict())
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=e.status_code or 404, detail=e.to_dict())
    except ExternalAPIError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=e.to_dict())
    except RateLimitError as e:
        raise HTTPException(status_code=e.status_code or 429, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "InternalError", "message": str(e)})


@router.get("/{name}/with-abilities")
@handle_exceptions
async def get_pokemon_with_abilities(
    request: Request,
    name: str,
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Get pokemon with detailed ability information."""
    rate_limit(request)
    if hasattr(service, 'get_pokemon_with_abilities'):
        result = await service.get_pokemon_with_abilities(name)
    else:
        result = await service.get_pokemon_info(name)
    return result


@router.get("/{name}/summary")
@handle_exceptions
async def get_pokemon_summary(
    request: Request,
    name: str,
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    rate_limit(request)
    if hasattr(service, 'get_pokemon_summary'):
        return await service.get_pokemon_summary(name)
    return await service.get_pokemon_info(name)


@router.get("/type/{type_name}/summary")
@handle_exceptions
async def get_type_summary(
    request: Request,
    type_name: str,
    limit: int = Query(default=10, ge=1, le=50),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    rate_limit(request)
    if hasattr(service, 'get_type_summary'):
        return await service.get_type_summary(type_name, limit=limit)
    raise HTTPException(status_code=501, detail="Type summary not implemented")


@router.get("/compare")
@handle_exceptions
async def compare_pokemons(
    request: Request,
    first: str = Query(..., description="First pokemon name"),
    second: str = Query(..., description="Second pokemon name"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    rate_limit(request)
    if hasattr(service, 'compare_pokemons'):
        return await service.compare_pokemons(first, second)
    raise HTTPException(status_code=501, detail="Compare not implemented")


@router.get("/cache/stats")
async def cache_stats(cache: ICache = Depends(get_cache)) -> Dict[str, Any]:
    if hasattr(cache, 'stats'):
        return cache.stats()
    return {"message": "Stats not available"}


@router.get("/rate/status")
async def rate_status_endpoint(request: Request) -> Dict[str, Any]:
    return rate_status(request)


@router.post("/group/by-type")
@handle_exceptions
async def group_by_type(
    request: Request,
    pokemon_names: List[str] = Body(..., description="List of Pokémon names to group"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Group Pokémon by their primary type with markdown table."""
    rate_limit(request)
    if hasattr(service, 'group_pokemons_by_type'):
        return await service.group_pokemons_by_type(pokemon_names)
    raise HTTPException(status_code=501, detail="Grouping not implemented")


@router.post("/classify/by-role")
@handle_exceptions
async def classify_by_role(
    request: Request,
    pokemon_names: List[str] = Body(..., description="List of Pokémon names to classify"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Classify Pokémon by battle role based on stats."""
    rate_limit(request)
    if hasattr(service, 'classify_by_role'):
        return await service.classify_by_role(pokemon_names)
    raise HTTPException(status_code=501, detail="Classification not implemented")


@router.post("/team/strength")
@handle_exceptions
async def calculate_team_strength(
    request: Request,
    pokemon_names: List[str] = Body(..., description="List of Pokémon names (max 6)"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Calculate team strength and synergies."""
    rate_limit(request)
    if hasattr(service, 'calculate_team_strength'):
        return await service.calculate_team_strength(pokemon_names)
    raise HTTPException(status_code=501, detail="Team strength calculation not implemented")


@router.post("/team/recommend")
@handle_exceptions
async def recommend_team(
    request: Request,
    available_pokemon: List[str] = Body(..., description="Available Pokémon names"),
    opponent_types: List[str] | None = Body(None, description="Expected opponent types"),
    team_size: int = Body(6, ge=1, le=6, description="Team size"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Recommend optimal team composition for battle."""
    rate_limit(request)
    if hasattr(service, 'recommend_team_for_battle'):
        return await service.recommend_team_for_battle(
            available_pokemon=available_pokemon,
            opponent_types=opponent_types,
            team_size=team_size
        )
    raise HTTPException(status_code=501, detail="Team recommendation not implemented")


@router.get("/generation/compare")
@handle_exceptions
async def compare_generations(
    request: Request,
    generation_ids: List[str] = Query(None, description="Generation IDs to compare (default: 1,2,3)"),
    criteria: str = Query("variety", description="Comparison criteria: variety, stats, or count"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Compare Pokémon generations by various criteria."""
    rate_limit(request)
    if hasattr(service, 'compare_generations'):
        return await service.compare_generations(
            generation_ids=generation_ids,
            criteria=criteria
        )
    raise HTTPException(status_code=501, detail="Generation comparison not implemented")


@router.post("/personality/analyze")
@handle_exceptions
async def analyze_personality(
    request: Request,
    battle_style: str = Body(..., description="Battle style: aggressive, defensive, balanced, or tactical"),
    preferred_stat: str = Body(..., description="Preferred stat: hp, attack, defense, special-attack, special-defense, or speed"),
    element_preference: str = Body("any", description="Element preference: fire, water, grass, or any"),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Analyze personality based on Pokemon starter preferences.
    
    This endpoint analyzes all official starter Pokemon and determines your personality
    based on your battle style, preferred stat, and element preference.
    
    Personality is mapped from Pokemon statistics:
    - High HP -> Resilient, Patient, Enduring
    - High Attack -> Assertive, Direct, Competitive
    - High Defense -> Cautious, Protective, Strategic
    - High Special Attack -> Creative, Intellectual, Innovative
    - High Special Defense -> Composed, Stable, Thoughtful
    - High Speed -> Energetic, Adaptable, Quick-thinking
    """
    rate_limit(request)
    
    # Validate inputs
    valid_battle_styles = ["aggressive", "defensive", "balanced", "tactical"]
    valid_stats = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
    valid_elements = ["fire", "water", "grass", "any"]
    
    if battle_style not in valid_battle_styles:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ValidationError",
                "message": f"Invalid battle_style. Must be one of: {', '.join(valid_battle_styles)}",
                "field": "battle_style",
                "value": battle_style
            }
        )
    
    if preferred_stat not in valid_stats:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ValidationError",
                "message": f"Invalid preferred_stat. Must be one of: {', '.join(valid_stats)}",
                "field": "preferred_stat",
                "value": preferred_stat
            }
        )
    
    if element_preference not in valid_elements:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ValidationError",
                "message": f"Invalid element_preference. Must be one of: {', '.join(valid_elements)}",
                "field": "element_preference",
                "value": element_preference
            }
        )
    
    preferences = {
        "battle_style": battle_style,
        "preferred_stat": preferred_stat,
        "element_preference": element_preference
    }
    
    if hasattr(service, 'analyze_personality_from_starters'):
        return await service.analyze_personality_from_starters(preferences)
    raise HTTPException(status_code=501, detail="Personality analysis not implemented")


@router.post("/personality/analyze-from-text")
@handle_exceptions
async def analyze_personality_from_text(
    request: Request,
    payload: Dict[str, str] = Body(...),
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    """Analyze personality from natural language text.
    
    This endpoint uses AI to interpret free-form text and extract personality preferences,
    then matches you with a Pokemon starter.
    
    Example texts:
    - "I'm very competitive and always rush into challenges. I love the thrill of action!"
    - "I prefer to think things through carefully and protect what's important to me."
    - "I value creativity and finding unique solutions. I'm passionate and energetic."
    - "I'm adaptable and balanced, I can handle any situation that comes my way."
    
    The AI will extract:
    - battle_style (aggressive, defensive, balanced, tactical)
    - preferred_stat (hp, attack, defense, special-attack, special-defense, speed)
    - element_preference (fire, water, grass, or any)
    
    Returns the same personality analysis as /personality/analyze plus interpretation details.
    """
    rate_limit(request)
    
    # Extract user_text from payload
    user_text = payload.get("user_text", "")
    if not user_text:
        raise HTTPException(status_code=422, detail="user_text is required in the request body")
    
    # Import interpreter
    from services.personality_interpreter import get_personality_interpreter
    
    # Extract preferences from text
    interpreter = get_personality_interpreter()
    extraction = await interpreter.interpret_user_text(user_text)
    
    # Get personality analysis
    preferences = {
        "battle_style": extraction["battle_style"],
        "preferred_stat": extraction["preferred_stat"],
        "element_preference": extraction["element_preference"]
    }
    
    if hasattr(service, 'analyze_personality_from_starters'):
        result = await service.analyze_personality_from_starters(preferences)
        
        # Add interpretation metadata
        result["interpretation"] = {
            "original_text": user_text,
            "extracted_preferences": preferences,
            "confidence": extraction.get("confidence", "medium"),
            "reasoning": extraction.get("reasoning", "")
        }
        
        return result
    
    raise HTTPException(status_code=501, detail="Personality analysis not implemented")


# Place generic name route last to avoid shadowing more specific endpoints like /compare
@router.get("/{name}")
@handle_exceptions
async def get_pokemon(
    request: Request,
    name: str,
    service: IPokemonService = Depends(get_pokemon_service)
) -> Dict[str, Any]:
    rate_limit(request)
    result = await service.get_pokemon_info(name)
    return result
