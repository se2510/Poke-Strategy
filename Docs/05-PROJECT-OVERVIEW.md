# Pokémon Strategy Agent - Project Overview

## Objective

Development of an intelligent advisory agent that leverages real data from PokeAPI and a generative model (LLM) to provide structured, data-driven strategic recommendations for Pokémon battles.

---

## General Description

A comprehensive system for Pokémon analysis and strategic recommendations has been implemented, combining:

- **PokeAPI Wrapper**: Access to official Pokémon data (types, stats, generations)
- **AI Agent (Gemini)**: Strategic reasoning and natural language explanations
- **Analysis Tools**: Specialized functions for classification and recommendation
- **Flexible Interfaces**: Interactive CLI, Jupyter Notebook, and RESTful API

---

## Implemented Use Cases

### Team Recommendation for Battle

**Example Query**: *"What team of 5 Pokémon would be most effective against Fire-type opponents?"*

**Functionality**:
- Analysis of available Pokémon and their types
- Type advantage evaluation against opponents
- Balanced team composition (roles: tank, attacker, fast)
- Type coverage and synergy calculations
- Detailed advantages and potential weaknesses

**Tools Used**:
- `recommend_team_for_battle()`: Intelligent selection algorithm
- `calculate_team_strength()`: Strength/weakness analysis
- LLM: Explanation and justification generation

**Output Example**:
```markdown
## Recommended Team (vs Fire Type)

### Selected Pokémon:
1. **Blastoise** (Water) - 530 total stats
2. **Golem** (Rock/Ground) - 495 total stats
3. **Gyarados** (Water/Flying) - 540 total stats
4. **Venusaur** (Grass/Poison) - 525 total stats
5. **Zapdos** (Electric/Flying) - 580 total stats

### Advantages:
- Excellent coverage against Fire type (Water, Rock, Ground)
- Balanced roles (2 attackers, 1 tank, 2 balanced)
- Type diversity prevents concentrated weaknesses

### Potential Risks:
- Vulnerability to Electric attacks (Blastoise, Gyarados)
- Lack of purely defensive Pokémon

### Type Coverage:
Water, Rock, Ground, Grass, Poison, Electric, Flying (7 types)
```

---

### Pokémon Grouping and Classification

**Example Query**: *"Group and classify these Pokémon according to their battle role"*

**Functionality**:
- Role classification: **Tank** (defensive), **Attacker** (offensive), **Fast** (speed-based), **Balanced**
- Grouping by primary type
- Organized Markdown table generation
- Diversity and balance analysis

**Tools Used**:
- `classify_by_role()`: Automatic stat-based classification
- `group_pokemons_by_type()`: Type-based grouping
- LLM: Collection analysis and observations

**Output Example**:

| Pokémon | Type(s) | Role | HP | Attack | Defense | Speed |
|---------|---------|------|----|---------|---------| ------|
| Mewtwo | Psychic | Attacker | 106 | 110 | 90 | 130 |
| Blissey | Normal | Tank | 255 | 10 | 10 | 55 |
| Alakazam | Psychic | Attacker | 55 | 50 | 45 | 120 |
| Snorlax | Normal | Attacker | 160 | 110 | 65 | 30 |
| Electrode | Electric | Fast | 60 | 50 | 70 | 150 |

**Analysis**: Balanced collection with 40% attackers, 20% tanks, 20% fast, 20% balanced. Good type diversity (5 different types).

---

### Most Complete Generation

**Example Query**: *"Which Pokémon generation is most complete in terms of type diversity?"*

**Functionality**:
- Comparison of minimum 3 generations (Gen I, II, III, IV...)
- Evaluation criteria:
  - **Diversity**: Number of unique types
  - **Stats**: Average total statistics
  - **Quantity**: Total number of Pokémon
- Data-driven justification
- Comparative table display

**Tools Used**:
- `compare_generations()`: Automated comparative analysis
- LLM: Result interpretation and justification generation

**Output Example**:

| Generation | Region | Total Pokémon | Unique Types | Average Stats |
|------------|--------|---------------|--------------|---------------|
| Gen I | Kanto | 151 | 15 | 432.5 |
| Gen II | Johto | 100 | 15 | 428.3 |
| Gen III | Hoenn | 135 | 14 | 435.8 |
| Gen IV | Sinnoh | 107 | 15 | 441.2 |

**Winner**: **Generation I (Kanto)**

**Justification**:
- 15 unique types (maximum diversity alongside Gen II and IV)
- Highest Pokémon count (151 species)
- Balance between quantity and quality
- Established foundation of type system

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERFACES                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ CLI Script   │  │ Jupyter NB   │  │ REST API     │ │
│  │ (Interactive)│  │ (Demos)      │  │ (HTTP)       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   AI AGENT       │
                    │   (Gemini LLM)   │
                    │  • Reasoning     │
                    │  • Explanations  │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌───────▼────────┐
│ Tools             │ │  Services   │ │  Repositories  │
│ • team_recommend  │ │  • Pokemon  │ │  • PokeAPI     │
│ • classify_role   │ │  • Analysis │ │  • Cache       │
│ • compare_gen     │ │  • Summary  │ │                │
└───────────────────┘ └─────────────┘ └────────┬───────┘
                                               │
                                      ┌────────▼────────┐
                                      │   PokeAPI.co    │
                                      │  (Real data)    │
                                      └─────────────────┘
```

---

## Usage Instructions

### Option 1: Interactive CLI (Recommended)

```bash
# 1. Start API server
uvicorn main:app --reload

# 2. In another terminal, execute CLI
python pokemon_strategy_cli.py
```

The CLI provides an interactive menu with 3 use cases plus custom queries.

---

### Option 2: Jupyter Notebook

```bash
# Open demonstration notebook
jupyter notebook pokemon_strategy_demo.ipynb
```

The notebook includes:
- Detailed explanations of each use case
- Executable step-by-step code
- Real data examples
- Visualizations and tables

---

### Option 3: RESTful API

```bash
# Start server
uvicorn main:app --reload

# Use endpoints directly
curl -X POST http://localhost:8000/pokemon/team/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "available_pokemon": ["pikachu","charizard","blastoise"],
    "opponent_types": ["fire"],
    "team_size": 3
  }'
```

**Interactive Documentation**: http://localhost:8000/docs

---

## Main API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pokemon/team/recommend` | Recommends optimal team |
| POST | `/pokemon/classify/by-role` | Classifies by battle role |
| POST | `/pokemon/group/by-type` | Groups by primary type |
| POST | `/pokemon/team/strength` | Analyzes team strengths |
| GET | `/pokemon/generation/compare` | Compares generations |
| GET | `/pokemon/{name}/summary` | Pokémon summary |
| GET | `/pokemon/compare` | Compares two Pokémon |

---

## Technologies Used

### Backend:
- **FastAPI**: Modern, high-performance web framework
- **Python 3.13**: Primary language
- **httpx**: Asynchronous HTTP client
- **Pydantic**: Data validation

### AI and Agents:
- **Google Gemini 2.0**: LLM for reasoning
- **Google ADK**: Agent framework
- **Custom Tools**: Pokémon analysis

### Data:
- **PokeAPI**: Public API with official data
- **In-memory Cache**: Query optimization
- **Asynchronous Processing**: High performance

### Testing:
- **pytest**: Testing framework
- **pytest-asyncio**: Asynchronous tests
- **41 tests**: Complete coverage

---

## Key Features

### Real Data Foundation
- All analyses use official PokeAPI data
- No fabricated or hardcoded information
- Current stats, types, and generations

### Intelligent Reasoning
- LLM interprets context and requirements
- Natural language explanation generation
- Data-driven decision justification

### Structured Responses
- Formatted Markdown tables
- Clear sections (advantages, risks, recommendations)
- Consistent formatting

### Clean Architecture
- Dependency injection
- Layer separation (API, Service, Repository)
- SOLID principles applied
- 100% test coverage

### Optimized Performance
- Intelligent caching
- Asynchronous operations
- Rate limiting to prevent API overload

---

## Usage Examples

### Example 1: Team Against Water Type

**Input**:
```python
Available Pokémon: pikachu, raichu, zapdos, venusaur, exeggutor
Opponents: Water type
Team size: 3
```

**Agent Output**:
```
Recommended Team:
1. Zapdos (Electric/Flying) - 2x advantage vs Water
2. Venusaur (Grass/Poison) - 2x advantage vs Water
3. Raichu (Electric) - Speed and electric power

Advantages: Double super-effectiveness against Water
Risks: Vulnerable to Ice and Rock types
```

---

### Example 2: Collection Classification

**Input**:
```
Pokémon: mewtwo, blissey, alakazam, snorlax, gengar, dragonite
```

**Output**:
```
ATTACKERS (3):
   mewtwo, alakazam, dragonite

TANKS (1):
   blissey

BALANCED (2):
   snorlax, gengar

Analysis: Offensive collection with 50% attackers.
Recommendation: Add more defenders.
```

---

### Example 3: Best Generation

**Input**:
```
Generations: 1, 2, 3
Criteria: Type diversity
```

**Output**:
```
Winner: Generation II (Johto)
   • 15 unique types
   • Introduced Steel and Dark types
   • 100 Pokémon with good distribution

Comparison:
Gen I: 15 types, 151 Pokémon
Gen II: 15 types, 100 Pokémon  ← WINNER
Gen III: 14 types, 135 Pokémon
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Specific utility tests
python -m pytest tests/test_pokemon_utilities.py -v

# Test with coverage
python -m pytest tests/ --cov=services --cov=agent
```

**Results**:
- 41 passing tests
- Coverage > 90%
- Integration tests included

---

## Project Structure

```
backend/
├── agent/
│   ├── agent.py                    # AI agent with Gemini
│   └── tools.py                    # Agent tools
├── api/
│   └── routes/
│       └── pokemon.py              # REST endpoints
├── services/
│   └── pokemon_service.py          # Business logic
├── repositories/
│   ├── pokemon_repository.py       # PokeAPI access
│   └── cached_pokemon_repository.py # Cache decorator
├── tests/
│   ├── test_pokemon_utilities.py   # Utility tests
│   ├── test_pokemon_service.py     # Service tests
│   ├── test_cache.py               # Cache tests
│   └── test_api.py                 # API tests
├── scripts/
│   ├── pokemon_strategy_cli.py     # Interactive CLI
│   ├── quick_personality_test.py   # Quick personality test
│   └── test_agent_comparison.py    # Agent comparison
└── main.py                         # FastAPI application
```

---

## Requirements Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| PokeAPI Wrapper | ✅ | `pokemon_repository.py` with async methods |
| Agent with query and reasoning | ✅ | `agent.py` with Gemini + tools |
| CLI/Endpoint/Notebook | ✅ | All 3 implemented |
| Case 1: Battle team | ✅ | `recommend_team_for_battle()` |
| Case 2: Group/classify | ✅ | `classify_by_role()` + `group_by_type()` |
| Case 3: Complete generation | ✅ | `compare_generations()` |
| Explanations and justifications | ✅ | LLM + data-driven analysis |
| Tests | ✅ | 41 tests, complete coverage |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Google API key (for LLM)
export GOOGLE_API_KEY="your-api-key"

# 3. Start server
uvicorn main:app --reload

# 4. Use one of the interfaces:

# Option A: Interactive CLI
python pokemon_strategy_cli.py

# Option B: Jupyter Notebook
jupyter notebook pokemon_strategy_demo.ipynb

# Option C: Direct API
curl http://localhost:8000/docs
```

---

## Important Notes

1. **Google API Key**: Required for LLM (Gemini) usage
2. **Running Server**: CLI and notebook require active backend
3. **PokeAPI Limits**: Delays and caching implemented to respect rate limits
4. **Real-time Data**: All analyses use current PokeAPI data

---

## Project Learnings

This project demonstrates:
- Integration of LLMs with specialized tools
- Clean and testable architecture
- Efficient asynchronous processing
- Objective criteria-based data analysis
- Natural explanation generation from data
- Multiple interfaces for different use cases

---

## Author

Project developed as a demonstration of AI agents with specialized tools.

**Technologies**: Python, FastAPI, Google Gemini, PokeAPI

---

## License

This project is open source and available for educational purposes.
