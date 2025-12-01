import httpx
from typing import Dict, Any, List

API_BASE_URL = "http://localhost:8000"


async def get_pokemon_summary(pokemon_name: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/pokemon/{pokemon_name}/summary")
        resp.raise_for_status()
        return resp.json()


async def get_pokemon(pokemon_name: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/pokemon/{pokemon_name}")
        resp.raise_for_status()
        return resp.json()


async def get_type_summary(type_name: str, limit: int = 10) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/pokemon/type/{type_name}/summary", params={"limit": limit})
        resp.raise_for_status()
        return resp.json()


async def compare_pokemons(first: str, second: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/pokemon/compare", params={"first": first, "second": second})
        resp.raise_for_status()
        return resp.json()


async def group_pokemons_by_type(pokemon_names: List[str]) -> Dict[str, Any]:
    """Group Pokémon by their primary type with markdown visualization.
    
    Args:
        pokemon_names: List of Pokémon names to group
        
    Returns:
        Dictionary with groups, summaries, and markdown table
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/pokemon/group/by-type",
            json=pokemon_names
        )
        resp.raise_for_status()
        return resp.json()


async def classify_by_role(pokemon_names: List[str]) -> Dict[str, Any]:
    """Classify Pokémon by battle role (tank, attacker, fast, balanced).
    
    Args:
        pokemon_names: List of Pokémon names to classify
        
    Returns:
        Dictionary with role classifications and markdown table
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/pokemon/classify/by-role",
            json=pokemon_names
        )
        resp.raise_for_status()
        return resp.json()


async def calculate_team_strength(pokemon_names: List[str]) -> Dict[str, Any]:
    """Calculate team strength, synergies, and provide recommendations.
    
    Args:
        pokemon_names: List of Pokémon names (max 6 for standard team)
        
    Returns:
        Team analysis with strengths, weaknesses, and recommendations
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/pokemon/team/strength",
            json=pokemon_names
        )
        resp.raise_for_status()
        return resp.json()


async def recommend_team_for_battle(
    available_pokemon: List[str],
    opponent_types: List[str] | None = None,
    team_size: int = 6
) -> Dict[str, Any]:
    """Recommend optimal team composition for battle.
    
    Args:
        available_pokemon: List of available Pokémon names
        opponent_types: Expected opponent types to counter (optional)
        team_size: Number of Pokémon to select (default 6)
        
    Returns:
        Recommended team with justification and analysis
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/pokemon/team/recommend",
            json={
                "available_pokemon": available_pokemon,
                "opponent_types": opponent_types,
                "team_size": team_size
            }
        )
        resp.raise_for_status()
        return resp.json()


async def compare_generations(
    generation_ids: List[str] | None = None,
    criteria: str = "variety"
) -> Dict[str, Any]:
    """Compare Pokémon generations by various criteria.
    
    Args:
        generation_ids: List of generation IDs (e.g., ["1", "2", "3"]). If None, compares first 3
        criteria: Comparison criteria - "variety" (type diversity), "stats" (avg stats), or "count" (number of Pokémon)
        
    Returns:
        Comparison results with winner justification and markdown report
    """
    async with httpx.AsyncClient() as client:
        params = {"criteria": criteria}
        if generation_ids:
            params["generation_ids"] = generation_ids
        
        resp = await client.get(
            f"{API_BASE_URL}/pokemon/generation/compare",
            params=params
        )
        resp.raise_for_status()
        return resp.json()


async def analyze_personality_from_preferences(
    battle_style: str,
    preferred_stat: str,
    element_preference: str = "any"
) -> Dict[str, Any]:
    """Analyze personality based on Pokemon starter preferences.
    
    This tool analyzes all official starter Pokemon across generations and
    determines personality traits based on user preferences and Pokemon statistics.
    
    Args:
        battle_style: Battle approach - "aggressive", "defensive", "balanced", or "tactical"
        preferred_stat: Most valued stat - "hp", "attack", "defense", "special-attack", "special-defense", or "speed"
        element_preference: Preferred element type - "fire", "water", "grass", or "any" (default: "any")
        
    Returns:
        Personality analysis with:
        - matched_starter: Best matching Pokemon starter
        - personality_traits: List of personality traits
        - trait_analysis: Detailed analysis of traits mapped from stats
        - summary: Complete markdown personality report
        - alternative_matches: Top 3 other matching starters
    
    Example:
        result = await analyze_personality_from_preferences(
            battle_style="aggressive",
            preferred_stat="speed",
            element_preference="fire"
        )
        # Returns personality analysis with Charmander/Torchic/similar as match
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/pokemon/personality/analyze",
            json={
                "battle_style": battle_style,
                "preferred_stat": preferred_stat,
                "element_preference": element_preference
            }
        )
        resp.raise_for_status()
        return resp.json()


async def analyze_personality_from_text(user_text: str) -> Dict[str, Any]:
    """Analyze personality from natural language description.
    
    This tool uses AI to interpret free-form text about the user's personality,
    preferences, or how they approach challenges, then matches them with a
    Pokemon starter and reveals personality traits.
    
    Args:
        user_text: Natural language description of personality, preferences, or approach to challenges.
                  Should be at least 10 characters. Examples:
                  - "I'm very competitive and always rush into challenges"
                  - "I prefer to think things through and protect what matters"
                  - "I value creativity and finding unique solutions"
                  - "I'm adaptable and can handle any situation"
    
    Returns:
        Personality analysis with:
        - matched_starter: Best matching Pokemon starter
        - personality_traits: List of personality traits
        - summary: Complete markdown personality report
        - interpretation: Details about how preferences were extracted from text
          - original_text: The input text
          - extracted_preferences: battle_style, preferred_stat, element_preference
          - confidence: high/medium/low
          - reasoning: Why these preferences were chosen
    
    Example:
        result = await analyze_personality_from_text(
            "I love taking risks and being the first to try new things. "
            "Speed and agility are my strengths!"
        )
        # Returns personality analysis with interpretation details
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/pokemon/personality/analyze-from-text",
            json={"user_text": user_text}
        )
        resp.raise_for_status()
        return resp.json()


TOOLS = {
    "get_pokemon_summary": get_pokemon_summary,
    "get_pokemon": get_pokemon,
    "get_type_summary": get_type_summary,
    "compare_pokemons": compare_pokemons,
    "group_pokemons_by_type": group_pokemons_by_type,
    "classify_by_role": classify_by_role,
    "calculate_team_strength": calculate_team_strength,
    "recommend_team_for_battle": recommend_team_for_battle,
    "compare_generations": compare_generations,
    "analyze_personality_from_preferences": analyze_personality_from_preferences,
    "analyze_personality_from_text": analyze_personality_from_text,
}
