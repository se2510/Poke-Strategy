# Personality Analysis Feature

Comprehensive guide to the Pokémon Personality Analysis system - An innovative feature of the Pokémon Strategy Agent.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [How It Works](#how-it-works)
4. [Stats to Personality Mapping](#stats-to-personality-mapping)
5. [CLI Usage](#cli-usage)
6. [API Usage](#api-usage)
7. [Agent Usage](#agent-usage)
8. [Examples](#examples)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Use Cases](#use-cases)
13. [Technical Details](#technical-details)
14. [References](#references)

---

## Overview

The **Personality Analysis** feature analyzes all official Pokémon starters (from Generation I to IX) and determines personality based on:

1. **Battle style** (aggressive, defensive, balanced, tactical)
2. **Most valued stat** (HP, Attack, Defense, Special Attack, Special Defense, Speed)
3. **Elemental preference** (Fire, Water, Grass, or any)

The system maps the stats of the starter Pokémon that best matches preferences to specific personality traits.

### Starter Pokémon Coverage

**Total: 27 Starters** across 9 generations:

- **Generation I (Kanto)**: Bulbasaur, Charmander, Squirtle
- **Generation II (Johto)**: Chikorita, Cyndaquil, Totodile
- **Generation III (Hoenn)**: Treecko, Torchic, Mudkip
- **Generation IV (Sinnoh)**: Turtwig, Chimchar, Piplup
- **Generation V (Unova)**: Snivy, Tepig, Oshawott
- **Generation VI (Kalos)**: Chespin, Fennekin, Froakie
- **Generation VII (Alola)**: Rowlet, Litten, Popplio
- **Generation VIII (Galar)**: Grookey, Scorbunny, Sobble
- **Generation IX (Paldea)**: Sprigatito, Fuecoco, Quaxly

---

## Features

### 1. Interactive Quiz Mode

A structured questionnaire with three key questions, available through the CLI.

#### Question 1: Battle Style
- **Aggressive**: Head-on approach, competitive, direct
- **Defensive**: Protective strategy, cautious, prepared
- **Balanced**: Adaptive style, versatile, moderate
- **Tactical**: Strategic thinking, creative, analytical

#### Question 2: Preferred Quality (Stat)
- **HP (Resilience)**: Endurance, stamina, persistence
- **Attack (Power)**: Strength, force, assertiveness
- **Defense (Protection)**: Safety, stability, reliability
- **Special Attack (Creativity)**: Innovation, intelligence, uniqueness
- **Special Defense (Composure)**: Emotional stability, calmness, wisdom
- **Speed (Agility)**: Quick-thinking, adaptability, energy

#### Question 3: Element Preference
- **Fire**: Passion and energy
- **Water**: Fluidity and adaptability
- **Grass**: Growth and harmony
- **Any**: Open to all elements

### 2. Free-Form Text Analysis (AI-Powered)

Allows users to describe themselves in natural language. The AI (Google Gemini) interprets the text and extracts:
- Battle style preferences
- Valued qualities (mapped to stats)
- Element affinity
- Confidence level of the interpretation
- Reasoning behind the extraction

**Example inputs:**
```
"I'm very competitive and always rush into challenges. I love the thrill of action!"
 Aggressive, Speed/Attack, Fire

"I prefer to think things through carefully and protect what's important to me."
 Defensive, Defense/HP, Water

"I value creativity and finding unique solutions. I'm passionate and energetic."
 Tactical, Special-Attack, Fire
```

### 3. Quick Demo Mode

Pre-configured personality profiles for quick testing:

1. **The Aggressive Speedster**: Fast and fierce, fire element
2. **The Defensive Tank**: Patient and protective, water element
3. **The Tactical Strategist**: Creative and strategic, grass element
4. **The Balanced Warrior**: Well-rounded and adaptable

---

## How It Works

### System Flow

```
User Input (CLI/API)
      
[Mode Selection: Quiz | Text | Demo]
      
[AI Text Interpretation] (if text mode)
      
[Preference Collection]
      
[Fetch All Starters] (27 Pokémon across 9 generations)
      
[Filter by Element] (optional)
      
[Score Based on Battle Style & Preferred Stat]
      
[Select Best Match]
      
[Map Stats  Personality Traits]
      
[Generate Personality Report]
```

### Scoring Algorithm

The system scores each starter based on:

1. **Battle Style Multipliers:**
   - **Aggressive**: Attack  2, Special Attack  2, Speed  1.5
   - **Defensive**: HP  2, Defense  2, Special Defense  2
   - **Tactical**: Special Attack  2, Special Defense  1.5, Speed  1.5
   - **Balanced**: Sum of all stats

2. **Preferred Stat Bonus:**
   - The preferred stat receives a  3 multiplier

3. **Element Filtering:**
   - If an element is specified, only starters of that type are considered

---

## Stats to Personality Mapping

### HP (Hit Points)  Resilience

**High HP indicates:**
- **Resilient**: Ability to recover from adversity
- **Patient**: Not rushed, takes time
- **Enduring**: Persists through prolonged challenges
- **Steadfast**: Firm in convictions
- **Durable**: Strong and lasting

**Description:**
> "You have great stamina and can handle prolonged challenges"

---

### Attack  Assertiveness

**High Attack indicates:**
- **Assertive**: Expresses opinions with confidence
- **Direct**: Gets straight to the point
- **Competitive**: Motivated by challenges and winning
- **Bold**: Not afraid to take risks
- **Powerful**: Strong and forceful

**Description:**
> "You tackle problems head-on with confidence and determination"

---

### Defense  Caution

**High Defense indicates:**
- **Cautious**: Thinks before acting
- **Protective**: Cares for what matters
- **Strategic**: Plans carefully
- **Reliable**: Others can count on you
- **Steadfast**: Firm and unwavering

**Description:**
> "You think before acting and protect what matters to you"

---

### Special Attack  Creativity

**High Special Attack indicates:**
- **Creative**: Thinks outside the box
- **Intellectual**: Values knowledge
- **Innovative**: Seeks new solutions
- **Visionary**: Sees possibilities others don't
- **Clever**: Quick-witted and ingenious

**Description:**
> "You approach challenges with unique and creative solutions"

---

### Special Defense  Composure

**High Special Defense indicates:**
- **Composed**: Remains calm under pressure
- **Stable**: Emotionally balanced
- **Thoughtful**: Reflects deeply
- **Wise**: Learns from experience
- **Calm**: Peaceful and controlled

**Description:**
> "You remain calm under pressure and think things through"

---

### Speed  Adaptability

**High Speed indicates:**
- **Energetic**: Full of energy and enthusiasm
- **Adaptable**: Adjusts quickly to changes
- **Quick-thinking**: Makes fast decisions
- **Dynamic**: Versatile and changing
- **Agile**: Nimble and responsive

**Description:**
> "You adapt quickly to change and think on your feet"

---

## CLI Usage

Access the personality test through the main CLI:

```bash
python scripts/pokemon_strategy_cli.py
# Select option [4] - Pokemon Personality Test
```

### Mode 1: Interactive Quiz
```bash
# Choose mode [1] - Interactive Quiz
# Answer the three questions:
#   1. Battle Style (Aggressive/Defensive/Balanced/Tactical)
#   2. Preferred Quality (HP/Attack/Defense/Sp.Atk/Sp.Def/Speed)
#   3. Element Preference (Fire/Water/Grass/Any)
# View your personality match!
```

### Mode 2: Free-Form Text
```bash
# Choose mode [2] - Free-form Text
# Enter a description of yourself (min 10 characters)
# Example: "I'm someone who values intelligence and creativity..."
# AI extracts preferences and shows interpretation
# View results with AI reasoning
```

### Mode 3: Quick Demo
```bash
# Choose mode [3] - Quick Demo
# Select a predefined profile (1-4)
# Instantly see results
```

---

## API Usage

### Endpoint 1: Structured Analysis

```
POST /pokemon/personality/analyze
```

**Request Body:**
```json
{
  "battle_style": "aggressive",
  "preferred_stat": "speed",
  "element_preference": "fire"
}
```

**Parameters:**

| Parameter | Type | Valid Values | Description |
|-----------|------|--------------|-------------|
| `battle_style` | string | `aggressive`, `defensive`, `balanced`, `tactical` | Approach to challenges |
| `preferred_stat` | string | `hp`, `attack`, `defense`, `special-attack`, `special-defense`, `speed` | Most valued stat |
| `element_preference` | string | `fire`, `water`, `grass`, `any` | Preferred element (optional) |

**Response:**
```json
{
  "matched_starter": "charmander",
  "match_score": 87.5,
  "starter_details": {
    "id": 4,
    "name": "charmander",
    "types": ["fire"],
    "stats": {
      "hp": 39,
      "attack": 52,
      "defense": 43,
      "special-attack": 60,
      "special-defense": 50,
      "speed": 65
    }
  },
  "personality_traits": [
    "Energetic",
    "Adaptable",
    "Quick-thinking",
    "Creative",
    "Intellectual",
    "Assertive"
  ],
  "trait_analysis": [
    {
      "stat": "Speed",
      "value": 65,
      "traits": ["Energetic", "Adaptable", "Quick-thinking", "Dynamic"],
      "description": "You adapt quickly to change and think on your feet"
    }
  ],
  "alternative_matches": [
    {"name": "torchic", "score": 85.0},
    {"name": "chimchar", "score": 82.5}
  ],
  "summary": "# Your Pokemon Personality: Charmander..."
}
```

### Endpoint 2: AI Text Analysis

```
POST /pokemon/personality/analyze-from-text
```

**Request Body:**
```json
{
  "user_text": "I'm very competitive and love taking on challenges directly!"
}
```

**Response:**
```json
{
  "matched_starter": "charmander",
  "match_score": 92,
  "personality_traits": [...],
  "interpretation": {
    "original_text": "I'm very competitive...",
    "extracted_preferences": {
      "battle_style": "aggressive",
      "preferred_stat": "attack",
      "element_preference": "fire"
    },
    "confidence": "high",
    "reasoning": "Strong indicators of competitive and aggressive traits..."
  }
}
```

---

## Agent Usage

The agent has the `analyze_personality_from_preferences` tool available for natural language queries.

### Query Examples

```python
# Example 1: Direct analysis
query = """
I want to discover my Pokemon personality. 
I have an aggressive battle style, I value speed the most, 
and I prefer fire-type Pokemon.
"""

# Example 2: Interactive guide
query = """
I'd like to know what Pokemon represents my personality, 
but I'm not sure how to describe myself. Can you help me?
"""

# Example 3: Comparison
query = """
Can you compare the personality traits of someone who prefers:
1. Defensive battle style with high HP
2. Aggressive style with high attack
3. Tactical style with high special attack
"""
```

### Programmatic Usage

```python
from agent.agent import root_agent

async for chunk in root_agent.generate_content_stream(
    "What Pokemon starter matches my personality if I'm tactical and value special attack?"
):
    if hasattr(chunk, 'text'):
        print(chunk.text, end='', flush=True)
```

---

## Examples

### Example 1: Aggressive Profile

**Input:**
```json
{
  "battle_style": "aggressive",
  "preferred_stat": "attack",
  "element_preference": "fire"
}
```

**Output:**
```
Matched Starter: Torchic
Match Score: 88.5
Personality Traits: Assertive, Direct, Competitive, Bold, Energetic, Creative

Top Stats:
1. Attack (60)  Assertive, Direct, Competitive, Bold
2. Special Attack (70)  Creative, Intellectual, Innovative
3. Speed (45)  Energetic, Adaptable

Why Torchic matches you:
- Your aggressive battle style aligns with Torchic's offensive capabilities
- Your preference for Fire-type aligns with Torchic's elemental nature
- You prioritize Attack, which is one of Torchic's strongest attributes
```

---

### Example 2: Defensive Profile

**Input:**
```json
{
  "battle_style": "defensive",
  "preferred_stat": "hp",
  "element_preference": "water"
}
```

**Output:**
```
Matched Starter: Squirtle
Match Score: 85.0
Personality Traits: Resilient, Patient, Enduring, Cautious, Protective, Composed

Top Stats:
1. Defense (65)  Cautious, Protective, Strategic, Reliable
2. Special Defense (64)  Composed, Stable, Thoughtful, Wise
3. HP (44)  Resilient, Patient, Enduring

Why Squirtle matches you:
- Your defensive approach matches Squirtle's resilient nature
- Your preference for Water-type aligns with Squirtle's elemental nature
- You prioritize HP, which reflects Squirtle's enduring qualities
```

---

### Example 3: Tactical Profile

**Input:**
```json
{
  "battle_style": "tactical",
  "preferred_stat": "special-attack",
  "element_preference": "grass"
}
```

**Output:**
```
Matched Starter: Bulbasaur
Match Score: 90.0
Personality Traits: Creative, Intellectual, Innovative, Composed, Stable, Cautious

Top Stats:
1. Special Attack (65)  Creative, Intellectual, Innovative, Visionary
2. Special Defense (65)  Composed, Stable, Thoughtful, Wise
3. Defense (49)  Cautious, Protective, Strategic

Why Bulbasaur matches you:
- Your tactical mindset resonates with Bulbasaur's strategic strengths
- Your preference for Grass-type aligns with Bulbasaur's elemental nature
- You prioritize Special Attack, which is one of Bulbasaur's strongest attributes
```

---

### Example 4: Free-Form Text Analysis

**Input:**
```
"I'm someone who values intelligence and creativity. I like to solve problems 
with unique approaches rather than brute force. I prefer to think strategically."
```

**AI Interpretation:**
```json
{
  "extracted_preferences": {
    "battle_style": "tactical",
    "preferred_stat": "special-attack",
    "element_preference": "grass"
  },
  "confidence": "high",
  "reasoning": "User emphasizes intelligence, creativity, and strategic thinking, 
  which strongly indicate tactical style with special-attack preference."
}
```

**Matched Starter:** Bulbasaur (Match Score: 89.5)

---

## Testing

Unit tests cover all functionality:

```python
# Test 1: Successful analysis
test_analyze_personality_from_starters_success()

# Test 2: Empty preferences validation
test_analyze_personality_empty_preferences()

# Test 3: Balanced battle style
test_analyze_personality_balanced_style()

# Test 4: AI text interpretation
test_personality_interpreter_success()
```

**Run tests:**
```bash
# All personality tests
pytest tests/test_pokemon_service.py -k "personality" -v
pytest tests/test_personality_interpreter.py -v

# Specific test
pytest tests/test_pokemon_service.py::test_analyze_personality_from_starters_success -v
```

---

## Troubleshooting

### Common Issues

**1. API Connection Error**
```
[ERROR] Cannot connect to API server
```
**Solution**: Ensure the FastAPI server is running:
```bash
uvicorn main:app --reload
```

**2. Empty Text Error**
```
[ERROR] Description too short. Please provide more detail.
```
**Solution**: Provide at least 10 characters with meaningful content.

**3. Invalid Choice**
```
[ERROR] Invalid choice. Please enter 1, 2, 3, or 4.
```
**Solution**: Enter only the number corresponding to your choice.

**4. AI Interpretation Failure**
```
[ERROR] Could not parse AI response
```
**Solution**: Rephrase your description with clearer personality indicators.

**5. Missing API Key**
```
[ERROR] GOOGLE_API_KEY not found
```
**Solution**: Set your Google API key in the `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

---

## Best Practices

### For CLI Implementation

1. **Input Validation**
   - Always validate user choices against allowed options
   - Provide clear error messages for invalid inputs
   - Use while loops for retry logic

2. **User Experience**
   - Clear visual separators (70 character lines)
   - Consistent formatting with brackets for labels: `[LABEL]`
   - Progress indicators during API calls
   - Detailed error handling with actionable messages

3. **Error Handling**
   - Graceful degradation when API is unavailable
   - Specific error messages for different failure modes
   - Connection error handling with helpful instructions

4. **Modularity**
   - Separate functions for each mode (quiz, text, demo)
   - Reusable display functions for results
   - Clear separation of concerns

### For API Integration

1. **Timeout Configuration**
   - Use appropriate timeouts (30s for AI operations)
   - Handle timeout errors gracefully

2. **Response Validation**
   - Check status codes before processing
   - Validate JSON structure
   - Handle missing optional fields

3. **Async Operations**
   - Use `async with` for httpx.AsyncClient
   - Proper async/await patterns throughout

### For Code Quality

- Type hints throughout
- Comprehensive docstrings
- Error handling at multiple levels
- Input validation
- Modular design
- Clean separation of UI and logic

---

## Use Cases

### 1. Personalized Team Building
Use personality analysis to recommend teams that align with the player's natural style.

### 2. Gamified Self-Discovery
Educational tool to understand personality traits through Pokémon.

### 3. Community and Social
Share your "personality Pokémon" with friends and compare results.

### 4. Battle Coaching
Identify strengths and weaknesses in play style based on profile.

### 5. Educational Tool
Learn about Pokémon stats and types through self-assessment.

---

## Technical Details

### Dependencies
- `httpx`: Async HTTP client for API calls
- `asyncio`: Async/await support
- `google-genai`: Google Gemini AI for text interpretation
- Python 3.10+: Type hints and modern features

### Performance Considerations
- Async operations for non-blocking I/O
- Efficient API calls (single request per analysis)
- Minimal data transfer
- Response caching at service layer

### Code Organization
- `services/personality_test_service.py`: Core service logic
- `services/personality_interpreter.py`: AI text interpretation
- `services/personality_quiz_ui.py`: CLI UI components
- `services/personality_presenter.py`: Result presentation
- `services/personality_facade.py`: Orchestration layer

---

## References

- [API Reference](./04-API-REFERENCE.md#personality-analysis)
- [Agent Tools](./08-AGENT-TOOLS.md)
- [Testing Guide](./09-TESTING.md)
- [Project Structure](./03-PROJECT-STRUCTURE.md)

---

**Discover which Pokémon starter you are!** 
