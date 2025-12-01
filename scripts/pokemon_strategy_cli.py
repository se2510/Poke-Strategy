"""
Pokemon Strategy Agent - Interactive CLI
Mini-project: Strategy advisor agent that answers Pokemon battle questions

Refactored to follow Clean Architecture and SOLID principles.
CLI layer only handles menu navigation and delegates to service layer.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.agent import root_agent, query_agent
from agent.adk_agent import query_adk_agent  # ADK implementation
from agent.tools import (
    recommend_team_for_battle,
    classify_by_role,
    compare_generations,
    calculate_team_strength,
    group_pokemons_by_type
)
from services.personality_facade import get_personality_test_facade
from services.personality_quiz_ui import QuizInputHandler

# Global setting for agent implementation
USE_ADK_AGENT = False  # Set to True to use ADK Agent, False for direct GeminiClient


async def get_agent_response(query: str) -> str:
    """Get response from configured agent implementation.
    
    Args:
        query: User query
        
    Returns:
        Agent response
    """
    if USE_ADK_AGENT:
        return await query_adk_agent(query)
    else:
        return await query_agent(query)


def toggle_agent_implementation() -> None:
    """Toggle between ADK Agent and Direct GeminiClient."""
    global USE_ADK_AGENT
    USE_ADK_AGENT = not USE_ADK_AGENT
    
    agent_type = "Google ADK Agent" if USE_ADK_AGENT else "Direct GeminiClient"
    print(f"\n[SETTINGS] Switched to: {agent_type}")
    print()
    print("Differences:")
    if USE_ADK_AGENT:
        print("  ✓ Uses Google's Agent Development Kit")
        print("  ✓ Automatic tool management")
        print("  ✓ Built-in conversation memory")
        print("  ✓ Structured agent framework")
        print("  ⚠ Slightly slower (tool orchestration overhead)")
    else:
        print("  ✓ Direct Gemini API calls")
        print("  ✓ Full control over caching")
        print("  ✓ Faster response times")
        print("  ✓ Custom post-processing")
        print("  ⚠ Manual tool integration")
    print()


def print_header() -> None:
    """Display program header"""
    print("\n" + "="*70)
    print("POKEMON STRATEGY ADVISOR")
    print("="*70)
    print("AI-powered advisor for Pokemon battle strategy")
    agent_type = "Google ADK Agent" if USE_ADK_AGENT else "Direct Gemini Client"
    print(f"Using: {agent_type}")
    print()


def print_menu() -> None:
    """Display menu options"""
    print("\n[MENU] AVAILABLE USE CASES:")
    print()
    print("[1] Recommended Team for Combat")
    print("    -> Get optimal team to face specific types")
    print()
    print("[2] Group and Classify Pokemon")
    print("    -> Organize Pokemon by type or combat role")
    print()
    print("[3] Most Complete Generation")
    print("    -> Compare generations by different criteria")
    print()
    print("[6] Toggle Agent Implementation")
    agent_type = "ADK Agent" if USE_ADK_AGENT else "Direct Client"
    print(f"    -> Currently using: {agent_type}")
    print()
    print("[4] Personality Test - Discover Your Pokemon")
    print("    -> Interactive quiz to find which Pokemon matches your personality")
    print()
    print("[5] Custom Question")
    print("    -> Ask your own question to the agent")
    print()
    print("[0] Exit")
    print()


async def case_1_combat_team() -> None:
    """Case 1: Recommended team for combat"""
    print("\n" + "="*70)
    print("[1] RECOMMENDED TEAM FOR COMBAT")
    print("="*70)
    print()
    
    # Predefined or custom option
    print("Use predefined example? (y/n): ", end="")
    use_example = input().strip().lower()
    
    if use_example == 'y':
        # Predefined example
        query = """
        I need a team of 5 Pokemon to battle against Fire and Flying type opponents.
        
        Available Pokemon:
        - pikachu, raichu, zapdos, jolteon (electric)
        - squirtle, blastoise, gyarados, lapras (water)
        - geodude, onix, golem, rhydon (rock/ground)
        - bulbasaur, venusaur, exeggutor (grass)
        - snorlax, dragonite, mewtwo (legendary/powerful)
        
        Give me a balanced team and explain why each Pokemon was chosen.
        """
        
        available = [
            "pikachu", "raichu", "zapdos", "jolteon",
            "squirtle", "blastoise", "gyarados", "lapras",
            "geodude", "onix", "golem", "rhydon",
            "bulbasaur", "venusaur", "exeggutor",
            "snorlax", "dragonite", "mewtwo"
        ]
        opponent_types = ["fire", "flying"]
        team_size = 5
        
    else:
        # Custom
        print("\nAvailable Pokemon (comma-separated):")
        print("Example: pikachu,charizard,blastoise,snorlax")
        available_input = input("-> ").strip()
        available = [p.strip() for p in available_input.split(',')]
        
        print("\nOpponent types to face (optional, press Enter to skip):")
        print("Example: fire,water")
        opponent_input = input("-> ").strip()
        opponent_types = [t.strip() for t in opponent_input.split(',')] if opponent_input else None
        
        print("\nTeam size (1-6):")
        team_size = int(input("-> ").strip() or "6")
        
        query = f"""
        Recommend me a team of {team_size} Pokemon for combat.
        Available Pokemon: {', '.join(available)}
        {f'Opponent types: {", ".join(opponent_types)}' if opponent_types else ''}
        
        Provide:
        1. Recommended team
        2. Team advantages
        3. Possible weaknesses
        4. Type coverage analysis
        """
    
    print("\n[INFO] Analyzing and generating recommendation...")
    print("[LOADING] Please wait, this may take a few seconds...\n")
    
    # Use agent for analysis
    response = await get_agent_response(query)
    print(response)
    
    # Verification with direct tool
    print("\n" + "-"*70)
    print("[VERIFICATION] DIRECT TOOL CHECK")
    print("-"*70)
    
    try:
        recommendation = await recommend_team_for_battle(
            available_pokemon=available[:20],  # Limit to avoid too many calls
            opponent_types=opponent_types,
            team_size=min(team_size, 6)
        )
        
        print(f"\n[SUCCESS] Team recommended by tool:")
        for i, pokemon in enumerate(recommendation['recommended_team'], 1):
            print(f"   {i}. {pokemon.capitalize()}")
        
        print(f"\n[ANALYSIS] Team analysis:")
        analysis = recommendation['team_analysis']
        print(f"   Type coverage: {', '.join(analysis['type_coverage'])}")
        print(f"   Role distribution: {analysis['role_distribution']}")
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")


async def case_2_group_classify() -> None:
    """Case 2: Group and classify Pokemon"""
    print("\n" + "="*70)
    print("[2] GROUP AND CLASSIFY POKEMON")
    print("="*70)
    print()
    
    print("Use predefined example? (y/n): ", end="")
    use_example = input().strip().lower()
    
    if use_example == 'y':
        pokemon_list = [
            "mewtwo", "blissey", "alakazam", "snorlax", "gengar",
            "dragonite", "tyranitar", "machamp", "electrode",
            "steelix", "scizor", "heracross", "gardevoir"
        ]
        
        query = f"""
        I have these Pokemon: {', '.join(pokemon_list)}
        
        Please:
        1. Classify them by combat role (Tank, Attacker, Fast, Balanced)
        2. Group them by primary type
        3. Show a table with name, types, role and main stats
        4. Comment on the diversity and balance of the collection
        """
    else:
        print("\nPokemon list (comma-separated):")
        print("Example: pikachu,charizard,blastoise,snorlax")
        pokemon_input = input("-> ").strip()
        pokemon_list = [p.strip() for p in pokemon_input.split(',')]
        
        print("\nGrouping criterion?")
        print("1. Primary type")
        print("2. Combat role")
        print("3. Both")
        criterion = input("-> ").strip()
        
        query = f"""
        Analyze these Pokemon: {', '.join(pokemon_list)}
        
        Group and classify them according to the requested criterion.
        Show an organized table and comment on the collection.
        """
    
    print("\n[INFO] Analyzing collection...")
    print("[LOADING] Please wait, this may take a few seconds...\n")
    
    response = await get_agent_response(query)
    print(response)
    
    # Verification with tools
    print("\n" + "-"*70)
    print("[VERIFICATION] DETAILED CLASSIFICATION BY ROLE")
    print("-"*70)
    
    try:
        classification = await classify_by_role(pokemon_list)
        
        for role, pokemon in classification['roles'].items():
            role_label = {
                'tank': '[TANK]',
                'attacker': '[ATTACKER]',
                'fast': '[FAST]',
                'balanced': '[BALANCED]'
            }.get(role, '[ROLE]')
            print(f"\n{role_label} {role.upper()}:")
            print(f"   {', '.join(pokemon)}")
        
    except Exception as e:
        print(f"[ERROR] {e}")


async def case_3_complete_generation() -> None:
    """Case 3: Most complete generation"""
    print("\n" + "="*70)
    print("[3] MOST COMPLETE GENERATION")
    print("="*70)
    print()
    
    print("Use predefined example? (y/n): ", end="")
    use_example = input().strip().lower()
    
    if use_example == 'y':
        generations = ["1", "2", "3", "4"]
        criteria = "variety"
        
        query = """
        Compare the first 4 Pokemon generations (I, II, III, IV).
        
        Evaluate them according to:
        1. Type diversity (variety)
        2. Total number of Pokemon
        3. Average statistics
        
        Determine which is the most "complete" and justify with data.
        Show a comparative table.
        """
    else:
        print("\nGenerations to compare (comma-separated):")
        print("Example: 1,2,3")
        gen_input = input("-> ").strip()
        generations = gen_input.split(',')
        
        print("\nComparison criterion:")
        print("1. Type diversity (variety)")
        print("2. Average statistics (stats)")
        print("3. Pokemon count (count)")
        crit_choice = input("-> ").strip()
        
        criteria_map = {"1": "variety", "2": "stats", "3": "count"}
        criteria = criteria_map.get(crit_choice, "variety")
        
        query = f"""
        Compare Pokemon generations {', '.join(generations)}.
        
        Use as main criterion: {criteria}
        
        Determine which is the best and justify your choice with data.
        """
    
    print("\n[INFO] Comparing generations...")
    print("[LOADING] Please wait, this may take a few seconds...\n")
    
    response = await get_agent_response(query)
    print(response)
    
    # Verification with tool
    print("\n" + "-"*70)
    print("[VERIFICATION] DETAILED COMPARISON")
    print("-"*70)
    
    try:
        comparison = await compare_generations(
            generation_ids=generations,
            criteria=criteria
        )
        
        print(f"\n[WINNER]: {comparison['winner_name']}")
        print(f"   Criterion: {criteria}")
        print(f"   Score: {comparison['winner_score']}")
        
        print(f"\n[DATA] All generations:")
        for gen in comparison['comparison_data']:
            print(f"   • {gen['name']}: "
                  f"{gen['type_diversity']} types, "
                  f"{gen['total_pokemon']} Pokemon, "
                  f"avg stats: {gen['average_total_stats']}")
        
    except Exception as e:
        print(f"[ERROR] {e}")


async def case_4_custom() -> None:
    """Case 4: Custom question to agent"""
    print("\n" + "="*70)
    print("[5] CUSTOM QUESTION")
    print("="*70)
    print()
    
    print("Example questions:")
    print("• Which is the best Water-type Pokemon from the first generation?")
    print("• Compare Charizard vs Blastoise in combat terms")
    print("• Give me 3 defensive Pokemon that resist Electric attacks")
    print()
    
    print("Your question:")
    query = input("-> ").strip()
    
    if not query:
        print("[ERROR] Empty question")
        return
    
    print("\n[INFO] Processing question...")
    print("[LOADING] Please wait, this may take a few seconds...\n")
    print("-" * 70)
    
    try:
        response = await get_agent_response(query)
        print(response)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    
    print("-" * 70)


async def case_4_personality_test() -> None:
    """Case 4: Interactive personality test to discover your Pokemon match.
    
    Uses Facade pattern to delegate to modular personality test system.
    Follows Clean Architecture - CLI only handles menu, no business logic.
    """
    print("\n" + "="*70)
    print("[4] POKEMON PERSONALITY TEST")
    print("="*70)
    print()
    print("Discover which Pokemon starter matches your personality!")
    print("Your answers will be mapped to Pokemon statistics to reveal")
    print("your core personality traits.")
    print()
    
    # Get facade instance (dependency injection)
    facade = get_personality_test_facade()
    input_handler = QuizInputHandler()
    
    # Choose mode (UI layer only)
    mode = input_handler.get_mode_choice()
    
    # Delegate to appropriate facade method (business logic)
    if mode == "1":
        await facade.run_interactive_quiz()
    elif mode == "2":
        await facade.run_text_analysis()
    elif mode == "3":
        await facade.run_quick_demo()
    else:
        print("[ERROR] Invalid mode selection")


async def main() -> None:
    """Main CLI function"""
    print_header()
    
    # Verify API
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get("http://localhost:8000/health")
        print("[SUCCESS] API Server connected\n")
    except:
        print("[ERROR] API Server is not running")
        print("   Please start the server first:")
        print("   uvicorn main:app --reload\n")
        return
    
    while True:
        print_menu()
        
        choice = input("Select an option (0-6): ").strip()
        
        if choice == "0":
            print("\nGoodbye!")
            break
        elif choice == "1":
            await case_1_combat_team()
        elif choice == "2":
            await case_2_group_classify()
        elif choice == "3":
            await case_3_complete_generation()
        elif choice == "4":
            await case_4_personality_test()
        elif choice == "5":
            await case_4_custom()
        elif choice == "6":
            toggle_agent_implementation()
        else:
            print("[ERROR] Invalid option")
        
        print("\n" + "="*70)
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
