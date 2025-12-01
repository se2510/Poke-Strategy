# Pokémon Strategy Agent

An intelligent Pokémon analysis and strategic recommendation system powered by AI, combining real data from PokeAPI with advanced reasoning through Google Gemini.

## Overview

This project implements a comprehensive Pokémon strategy analysis and recommendation system that integrates:

- **PokeAPI Wrapper**: Access to real Pokémon data (types, stats, generations)
- **AI Agent (Gemini)**: Strategic reasoning and natural language explanations
- **Analysis Tools**: Specialized functions for classification and recommendation
- **Flexible Interfaces**: Interactive CLI and RESTful API
- **Personality Analysis**: AI-powered personality matching with Pokemon starters

## Key Features

- Intelligent AI Agent with Google Gemini 2.0 for strategic reasoning
- **Dual Agent Implementation**: Toggle between ADK Agent and Direct Client
- Personality Analysis to discover your Pokemon based on personality traits
- Team Analysis with recommendations based on real statistics
- Automatic Classification by battle role, type, and generation
- Complete REST API with fully documented endpoints
- Interactive CLI with user-friendly interface
- Fully Tested with 57 tests, >90% coverage
- High Performance through intelligent caching and async operations

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# Required: Get your API key at https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-api-key-here

# Optional (defaults shown)
CACHE_ENABLED=true
CACHE_TYPE=memory
DEBUG=true
```

### Running the Application

```bash
# Start API server
uvicorn main:app --reload

# In another terminal: Interactive CLI
python scripts/pokemon_strategy_cli.py

# Access API documentation
open http://localhost:8000/docs
```

## Use Cases

### 1. Team Recommendation for Battle

Recommend optimal Pokemon teams for specific battle scenarios.

**Example Request:**
```bash
POST /pokemon/team/recommend
{
  "available_pokemon": ["pikachu", "charizard", "blastoise", "venusaur"],
  "opponent_types": ["water", "rock"],
  "team_size": 3
}
```

**Features:**
- Analyzes available Pokemon and their types
- Considers type advantages against opponents
- Recommends balanced teams (roles: tank, attacker, fast)
- Calculates type coverage and synergies
- Explains advantages and potential weaknesses

### 2. Pokemon Classification

Group and classify Pokemon by battle role or type.

**Battle Roles:**
- **Tank**: High HP and Defense (defensive specialists)
- **Attacker**: High Attack or Special Attack (offensive powerhouses)
- **Fast**: High Speed (quick strikers)
- **Balanced**: Well-rounded stats

**Example Response:**
```
ATTACKERS (2): mewtwo, alakazam
TANKS (1): blissey
BALANCED (1): snorlax
```

### 3. Generation Comparison

Compare Pokemon generations by various criteria.

**Criteria:**
- **Diversity**: Number of unique types
- **Stats**: Average total statistics
- **Quantity**: Total number of Pokemon

**Example:**
```bash
GET /pokemon/generation/compare?generation_ids=1&generation_ids=2&criteria=variety
```

### 4. Personality Analysis

Discover which Pokemon starter matches your personality.

**Features:**
- Analyzes 27 Pokemon starters (Gen I-IX)
- Maps stats to personality traits (6 dimensions)
- AI interpretation of free-text descriptions
- Extracts battle style and element preferences

**Example:**
```bash
POST /pokemon/personality/analyze-from-text
{
  "user_text": "I like to be strategic and think before acting. I prefer good defense."
}
```

## Architecture

```
┌─────────────────────────────────────────┐
│     PRESENTATION LAYER                  │
│  API (FastAPI) | CLI                    │
└──────────┬──────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│     AGENT LAYER (AI Reasoning)          │
│  Gemini 2.0 + Custom Tools              │
└──────────┬──────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│     BUSINESS LOGIC LAYER                │
│  Pokemon Service + Validations          │
└──────────┬──────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│     DATA ACCESS LAYER                   │
│  Repository + Cache Decorator           │
└──────────┬──────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│     EXTERNAL SERVICES                   │
│  PokeAPI.co | Google AI (Gemini)        │
└─────────────────────────────────────────┘
```

**Design Principles:**
- Separation of Concerns (SoC)
- Dependency Inversion (DIP)
- Single Responsibility (SRP)
- Open/Closed (OCP)
- Liskov Substitution (LSP)

See [Architecture Details](./Docs/02-ARCHITECTURE.md)

## Technology Stack

### Backend
- **Python 3.13**: Primary language
- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation and settings
- **httpx**: Async HTTP client

### AI and Agents
- **Google Gemini 2.0**: LLM for reasoning
- **Google ADK**: Agent framework (dual implementation)
- **Direct Gemini Client**: High-performance alternative
- **Custom Tools**: Specialized Pokemon analysis

### Data and Cache
- **PokeAPI**: Official Pokemon data API
- **Redis** (optional): Distributed cache
- **In-Memory Cache**: Local caching

### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **57 tests**: 100% passing
- **>90% coverage**: High code quality

## API Endpoints

### Team Strategy
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pokemon/team/recommend` | Recommend optimal team |
| POST | `/pokemon/team/strength` | Analyze team strengths |
| POST | `/pokemon/classify/by-role` | Classify by battle role |
| POST | `/pokemon/group/by-type` | Group by primary type |

### Comparison and Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pokemon/generation/compare` | Compare generations |
| GET | `/pokemon/{name}/summary` | Pokemon summary |
| GET | `/pokemon/compare` | Compare two Pokemon |

### Personality Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pokemon/personality/analyze` | Structured preferences analysis |
| POST | `/pokemon/personality/analyze-from-text` | Natural language analysis (AI) |

### General
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pokemon/` | List Pokemon (paginated) |
| GET | `/pokemon/{name}` | Get specific Pokemon |
| GET | `/docs` | Interactive API documentation |
| GET | `/health` | Service health check |

**Interactive Documentation**: http://localhost:8000/docs

See [Complete API Reference](./Docs/04-API-REFERENCE.md)

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_pokemon_service.py -v

# Run personality tests (requires GOOGLE_API_KEY)
python -m pytest tests/test_personality_interpreter.py -v

# Run with coverage report
python -m pytest tests/ --cov=services --cov=agent --cov-report=html
```

**Test Results:**
- 57 tests, 100% passing
- Over 90% code coverage
- Includes integration tests

See [Testing Guide](./Docs/14-TESTING.md)

## Project Structure

```
backend/
├── agent/                          # AI agent and tools
│   ├── agent.py                    # Gemini agent configuration
│   └── tools.py                    # Specialized tools
├── api/                            # REST API
│   └── routes/
│       └── pokemon.py              # Pokemon endpoints
├── services/                       # Business logic
│   ├── pokemon_service.py          # Analysis and recommendations
│   └── personality_interpreter.py  # AI personality interpretation
├── repositories/                   # Data access
│   ├── pokemon_repository.py       # PokeAPI client
│   └── cached_pokemon_repository.py # Cache decorator
├── core/                           # Configuration and utilities
│   ├── config.py                   # Settings management
│   ├── dependencies.py             # DI container
│   └── interfaces.py               # Base interfaces
├── infrastructure/                 # Infrastructure services
│   ├── cache_factory.py            # Cache factory
│   ├── memory_cache.py             # In-memory cache
│   └── redis_cache.py              # Redis cache
├── tests/                          # Unit and integration tests
│   ├── test_pokemon_utilities.py   # Utility tests
│   ├── test_pokemon_service.py     # Service tests
│   ├── test_personality_interpreter.py # AI interpretation tests
│   ├── test_cache.py               # Cache tests
│   └── test_api.py                 # API tests
├── scripts/                        # CLI utilities
│   ├── pokemon_strategy_cli.py     # Interactive CLI
│   ├── quick_personality_test.py   # Quick personality test
│   ├── test_agent_comparison.py    # Agent comparison tool
│   └── README.md                   # Script documentation
├── Docs/                           # Complete documentation
│   ├── 11-PERSONALITY-ANALYSIS.md  # Personality analysis feature
│   ├── README.md                   # Documentation index
│   └── *.md                        # Additional guides
├── main.py                         # FastAPI application
├── requirements.txt                # Python dependencies
└── pytest.ini                      # Test configuration
```

See [Project Structure Details](./Docs/03-PROJECT-STRUCTURE.md)

## Documentation

### User Guides

| Document | Description |
|----------|-------------|
| [Quick Start](./Docs/01-QUICK-START.md) | Installation and setup guide |
| [Architecture](./Docs/02-ARCHITECTURE.md) | System design and components |
| [Project Structure](./Docs/03-PROJECT-STRUCTURE.md) | Code organization |
| [API Reference](./Docs/04-API-REFERENCE.md) | REST endpoint documentation |
| [Personality Analysis](./Docs/11-PERSONALITY-ANALYSIS.md) | Personality feature guide |

### Developer Guides

| Document | Description |
|----------|-------------|
| [Dependency Injection](./Docs/08-DEPENDENCY-INJECTION.md) | DI patterns and SOLID principles |
| [Caching](./Docs/09-CACHING.md) | Cache system (Memory/Redis) |
| [Testing Guide](./Docs/14-TESTING.md) | Testing strategies |
| [Agent Tools](./Docs/12-AGENT-TOOLS.md) | Custom tool development |
| [ADK Agent](./Docs/13-ADK-AGENT-IMPLEMENTATION.md) | ADK vs Direct Client comparison |

**Complete Index**: [Docs/README.md](./Docs/README.md)

## Configuration

### Environment Variables

```env
# Google AI (Required)
GOOGLE_API_KEY=your-api-key

# PokeAPI
POKEAPI_BASE_URL=https://pokeapi.co/api/v2
POKEAPI_TIMEOUT=10.0

# Cache
CACHE_ENABLED=true
CACHE_TYPE=memory  # or "redis"
CACHE_TTL=3600

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Application
DEBUG=true
```

## Requirements Met

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| PokeAPI Wrapper | ✓ | `pokemon_repository.py` with async methods |
| AI Agent with Reasoning | ✓ | `agent.py` with Gemini + tools |
| CLI/API/Notebook | ✓ | All three implemented |
| Team Battle Recommendations | ✓ | `recommend_team_for_battle()` |
| Group/Classify Pokemon | ✓ | `classify_by_role()` + `group_by_type()` |
| Generation Comparison | ✓ | `compare_generations()` |
| Personality Analysis | ✓ | `analyze_personality_from_starters()` + AI |
| Explanations and Justifications | ✓ | LLM + data-driven analysis |
| Tests | ✓ | 57 tests, complete coverage |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## AI Usage Disclosure

This project was developed with assistance from AI tools. For complete transparency on how AI was used, what code was generated vs. written manually, lessons learned, and risk mitigation strategies, see:

**📄 [AI_USAGE_DISCLOSURE.md](./AI_USAGE_DISCLOSURE.md)**

**Key Highlights:**
- **Roughly a third of code generated by AI** (boilerplate, tests, documentation)
- **Majority of code written manually** (business logic, architecture, algorithms)
- **Significant development time saved** while maintaining high code quality
- **All AI suggestions reviewed and validated** with comprehensive testing
- **Complete transparency** on accepted, modified, and rejected suggestions
- **Risk mitigation** through testing, validation, and human oversight

**What AI Helped With:**
- ✅ Boilerplate code generation (FastAPI endpoints, Pydantic models)
- ✅ Unit test generation (57 tests, >90% coverage)
- ✅ Documentation drafts (14 documents, 5,000+ lines)
- ✅ Code refactoring suggestions
- ✅ Debugging assistance

**What Was Done Manually:**
- 🎯 Core business logic (scoring algorithms, team recommendations)
- 🎯 Architectural decisions (Clean Architecture, SOLID principles)
- 🎯 Creative features (Personality Analysis system)
- 🎯 Domain expertise (Pokemon stats-to-traits mapping)
- 🎯 Quality assurance (code review, integration testing)

## License

This project is open source and available under the MIT License. See [LICENSE](./LICENSE) for details.

## Acknowledgments

- **PokeAPI**: For providing official Pokemon data
- **Google AI**: For the Gemini model and tools
- **FastAPI**: For the excellent web framework
- **Python Community**: For the amazing libraries

## Resources

### External Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [PokeAPI Documentation](https://pokeapi.co/docs/v2)
- [Google Gemini](https://ai.google.dev/docs)
- [Python Asyncio](https://docs.python.org/3/library/asyncio.html)

### Related Topics
- Clean Architecture in Python
- Dependency Injection Patterns
- API Design Best Practices
- AI Agents with Tools

---

**Build strategic Pokemon teams with the power of AI!**

[![Tests](https://img.shields.io/badge/tests-57%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-%3E90%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.13-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118-009688)]()
