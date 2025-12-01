# Quick Start Guide

This guide provides instructions for setting up and running the Pokémon Strategy Agent.

## Prerequisites

### Required
- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **pip** - Package manager (included with Python)
- **Google API Key** - Required for Gemini LLM ([Get here](https://makersuite.google.com/app/apikey))

### Optional
- **Redis** - For distributed cache (production)
- **Docker** - For containerization
- **Jupyter** - For running demo notebooks

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd backend
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Main dependencies installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client
- `pydantic` - Data validation
- `google-generativeai` - Gemini SDK
- `pytest` - Testing framework

---

## Configuration

### Step 1: Create Configuration File

```bash
# Copy template
cp .env.example .env

# Edit with preferred editor
nano .env  # or code .env
```

### Step 2: Configure Environment Variables

Open `.env` and configure:

```env
# === REQUIRED ===
GOOGLE_API_KEY="your-api-key-here"

# === OPTIONAL (default values) ===
# PokeAPI Configuration
POKEAPI_BASE_URL="https://pokeapi.co/api/v2"
POKEAPI_TIMEOUT=10.0

# Cache (memory by default, change to 'redis' in production)
CACHE_ENABLED=true
CACHE_TYPE="memory"
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Application
DEBUG=true
```

### Step 3: Obtain Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create new project (if needed)
4. Generate API Key
5. Copy and paste into `.env`

**Important:** API Keys should not be shared publicly.

---

## First Execution

### Option 1: REST API (Recommended)

```bash
# Start server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test the API:**

```bash
# Open in browser
http://localhost:8000/docs
```

Interactive Swagger UI documentation will be displayed.

### Option 2: Interactive CLI

```bash
# In another terminal (keep server running)
python pokemon_strategy_cli.py
```

**CLI Menu:**
```
Pokémon Strategy Agent - Interactive CLI
==========================================

Select an option:
1. Recommend team for battle
2. Group and classify Pokémon
3. Compare generations
4. Custom question
5. Exit

Option:
```

### Option 3: Jupyter Notebook

```bash
# Install Jupyter (if not installed)
pip install jupyter

# Start Jupyter
jupyter notebook pokemon_strategy_demo.ipynb
```

---

## Installation Verification

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Test 2: Get Pokémon

```bash
curl http://localhost:8000/pokemon/pikachu
```

**Expected response:**
```json
{
  "id": 25,
  "name": "pikachu",
  "types": ["electric"],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    ...
  }
}
```

### Test 3: Run Tests

```bash
pytest tests/ -v
```

**Expected result:**
```
============= test session starts =============
collected 41 items

tests/test_api.py::test_get_pokemon_success PASSED      [  2%]
tests/test_api.py::test_list_pokemons_success PASSED    [  4%]
...
============= 41 passed in 3.42s =============
```

---

## First Use - Practical Example

### Example 1: Recommend Team via CLI

```bash
python pokemon_strategy_cli.py
```

1. Select option `1` (Recommend team)
2. Enter available Pokémon: `pikachu,charizard,blastoise,venusaur,gengar`
3. Opponent types: `water,rock`
4. Team size: `3`

**Agent Response:**
```markdown
## Recommended Team

### Selected Pokémon:
1. **Pikachu** (Electric) - Advantage against Water
2. **Venusaur** (Grass/Poison) - Advantage against Water and Rock
3. **Gengar** (Ghost/Poison) - Versatility

### Advantages:
Excellent coverage against Water type
Balance of offensive and defensive roles
Type diversity

### Team Statistics:
- Average Attack: 95
- Average Defense: 78
- Average Speed: 102
```

### Example 2: Direct API Call

```bash
curl -X POST "http://localhost:8000/pokemon/team/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "available_pokemon": ["pikachu", "charizard", "blastoise"],
    "opponent_types": ["water"],
    "team_size": 2
  }'
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Invalid API Key"

**Solution:**
1. Verify key is in `.env`
2. Check for extra spaces
3. Regenerate key in Google AI Studio
4. Restart server

### Issue: "Connection refused to PokeAPI"

**Solution:**
```bash
# Verify internet connection
ping pokeapi.co

# Increase timeout in .env
POKEAPI_TIMEOUT=30.0
```

### Issue: Port 8000 in use

**Solution:**
```bash
# Use different port
uvicorn main:app --port 8001 --reload

# Or find and kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## Next Steps

With the project running, recommended next steps:

1. **[Project Architecture](./02-ARCHITECTURE.md)** - Understand system design
2. **[API Guide](./04-API-REFERENCE.md)** - Explore all endpoints
3. **[Use Cases](./13-USE-CASES.md)** - View complete examples
4. **[Testing](./14-TESTING.md)** - Learn to write tests

---

## Learning Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **PokeAPI Docs:** https://pokeapi.co/docs/v2
- **Google Gemini:** https://ai.google.dev/docs
- **Python Async/Await:** https://docs.python.org/3/library/asyncio.html

---

## Setup Complete

The Pokémon Strategy Agent is now running. Strategic team building can begin.

**Useful commands:**

```bash
# Start server
uvicorn main:app --reload

# Run CLI
python pokemon_strategy_cli.py

# Run tests
pytest tests/ -v

# View API documentation
http://localhost:8000/docs
```

---

**Issues? Consult [Troubleshooting](./10-TROUBLESHOOTING.md) or review logs.**
