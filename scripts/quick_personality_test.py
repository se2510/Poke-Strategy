"""
Quick Start Script for Pokemon Personality Test

This script provides a simple way to test the personality test feature
without going through the full CLI menu.
"""

import asyncio
import httpx
from typing import Dict, Any


async def quick_personality_test():
    """Run a quick personality test with default preferences."""
    print("=" * 70)
    print("QUICK POKEMON PERSONALITY TEST")
    print("=" * 70)
    print()
    
    # Check server
    print("Checking API server...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get("http://localhost:8000/health")
        print("✓ Server is running\n")
    except:
        print("✗ API Server is not running!")
        print("  Start it with: uvicorn main:app --reload")
        print()
        return
    
    # Predefined test cases
    test_cases = [
        {
            "name": "🔥 Fire Speedster",
            "emoji": "⚡",
            "preferences": {
                "battle_style": "aggressive",
                "preferred_stat": "speed",
                "element_preference": "fire"
            }
        },
        {
            "name": "💧 Water Tank",
            "emoji": "🛡️",
            "preferences": {
                "battle_style": "defensive",
                "preferred_stat": "hp",
                "element_preference": "water"
            }
        },
        {
            "name": "🌿 Grass Strategist",
            "emoji": "🧠",
            "preferences": {
                "battle_style": "tactical",
                "preferred_stat": "special-attack",
                "element_preference": "grass"
            }
        }
    ]
    
    print("Select a personality profile to test:")
    for i, test in enumerate(test_cases, 1):
        print(f"  [{i}] {test['name']} {test['emoji']}")
    print()
    
    choice = input("Your choice (1-3, or press Enter for all): ").strip()
    
    if choice and choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(test_cases):
            await run_single_test(test_cases[index])
        else:
            print("Invalid choice!")
    else:
        print("\nRunning all test cases...\n")
        for test in test_cases:
            await run_single_test(test)
            print()


async def run_single_test(test_case: Dict[str, Any]):
    """Run a single personality test."""
    print("-" * 70)
    print(f"Testing: {test_case['name']}")
    print("-" * 70)
    
    prefs = test_case['preferences']
    print(f"Battle Style: {prefs['battle_style'].title()}")
    print(f"Preferred Stat: {prefs['preferred_stat'].replace('-', ' ').title()}")
    print(f"Element: {prefs['element_preference'].title()}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/pokemon/personality/analyze",
                json=prefs
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✨ MATCHED POKEMON: {result['matched_starter'].upper()}")
                print(f"   Match Score: {result['match_score']}/100")
                print()
                
                print("Personality Traits:")
                for trait in result['personality_traits'][:5]:
                    print(f"   • {trait}")
                print()
                
                if result.get('alternative_matches'):
                    print("Top Alternatives:")
                    for alt in result['alternative_matches'][:3]:
                        print(f"   • {alt['name'].title()} - {alt['score']}/100")
                
                print("✓ Test passed!")
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"   {response.json()}")
                
    except Exception as e:
        print(f"✗ Error: {e}")


async def test_text_analysis():
    """Test the AI text analysis feature."""
    print("=" * 70)
    print("AI TEXT ANALYSIS TEST")
    print("=" * 70)
    print()
    
    test_texts = [
        "I'm very competitive and love rushing into challenges!",
        "I prefer to think things through and protect what matters.",
        "I value creativity and finding unique solutions to problems."
    ]
    
    print("Select a test text:")
    for i, text in enumerate(test_texts, 1):
        print(f"  [{i}] \"{text}\"")
    print(f"  [4] Custom text")
    print()
    
    choice = input("Your choice (1-4): ").strip()
    
    if choice == "4":
        text = input("\nEnter your text: ").strip()
    elif choice.isdigit() and 1 <= int(choice) <= 3:
        text = test_texts[int(choice) - 1]
    else:
        print("Invalid choice!")
        return
    
    print(f"\nAnalyzing: \"{text}\"\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/pokemon/personality/analyze-from-text",
                json={"user_text": text}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("AI INTERPRETATION:")
                interp = result.get('interpretation', {})
                prefs = interp.get('extracted_preferences', {})
                print(f"   Battle Style: {prefs.get('battle_style', 'N/A').title()}")
                print(f"   Preferred Stat: {prefs.get('preferred_stat', 'N/A').replace('-', ' ').title()}")
                print(f"   Element: {prefs.get('element_preference', 'N/A').title()}")
                print(f"   Confidence: {interp.get('confidence', 'N/A').upper()}")
                print()
                
                print(f"✨ MATCHED: {result['matched_starter'].upper()}")
                print(f"   Score: {result['match_score']}/100")
                print()
                print("✓ Test passed!")
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"   {response.json()}")
                
    except Exception as e:
        print(f"✗ Error: {e}")


async def main():
    """Main menu."""
    print()
    print("=" * 70)
    print("POKEMON PERSONALITY TEST - QUICK START")
    print("=" * 70)
    print()
    print("Choose test mode:")
    print("  [1] Quick Personality Test (structured)")
    print("  [2] AI Text Analysis Test")
    print("  [0] Exit")
    print()
    
    choice = input("Your choice: ").strip()
    
    if choice == "1":
        await quick_personality_test()
    elif choice == "2":
        await test_text_analysis()
    elif choice == "0":
        print("\nGoodbye!")
        return
    else:
        print("Invalid choice!")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
