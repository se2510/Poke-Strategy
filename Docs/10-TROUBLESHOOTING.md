# Troubleshooting

Common issues and debugging guide for the Pokémon Strategy Agent.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Errors](#configuration-errors)
3. [API Issues](#api-issues)
4. [Cache Errors](#cache-errors)
5. [AI Agent Issues](#ai-agent-issues)
6. [Testing Errors](#testing-errors)
7. [Performance Issues](#performance-issues)
8. [Logs and Debugging](#logs-and-debugging)

---

## Installation Issues

### Error: "ModuleNotFoundError"

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Dependencies not installed or virtual environment not activated.

**Solution:**
```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Verify installation
pip list | grep fastapi
```

---

### Error: "python: command not found"

**Symptom:**
```bash
bash: python: command not found
```

**Cause:** Python not installed or not in PATH.

**Solution:**
```bash
# Verify if Python is installed
python3 --version

# If installed, use python3
python3 -m venv venv

# Or add alias
alias python=python3
```

---

### Error: Incompatible Python Version

**Symptom:**
```
This project requires Python 3.13+
```

**Solution:**
```bash
# Verify version
python --version

# Install Python 3.13
# Windows: Download from python.org
# Linux: sudo apt install python3.13
# Mac: brew install python@3.13

# Create venv with specific version
python3.13 -m venv venv
```

---

## Configuration Errors

### Error: "GOOGLE_API_KEY not found"

**Symptom:**
```
ConfigurationError: GOOGLE_API_KEY environment variable not set
```

**Cause:** Environment variable not configured.

**Solution:**
```bash
# 1. Verify .env file exists
ls -la .env

# 2. If not exists, create from template
cp .env.example .env

# 3. Edit and add API key
nano .env  # or code .env

# 4. Verify it loaded
python -c "from core.config import Settings; print(Settings().GOOGLE_API_KEY[:10])"
```

---

### Error: "Invalid API Key"

**Symptom:**
```
ExternalAPIError: Invalid Google API Key
```

**Solution:**
```bash
# 1. Verify key in .env
cat .env | grep GOOGLE_API_KEY

# 2. Verify no extra quotes
# Correct:
GOOGLE_API_KEY=AIzaSy...

# Incorrect:
GOOGLE_API_KEY="AIzaSy..."

# 3. Regenerate key in Google AI Studio
# https://makersuite.google.com/app/apikey

# 4. Restart server
pkill -f uvicorn
uvicorn main:app --reload
```

---

### Error: Invalid Cache Type

**Symptom:**
```
ValueError: Invalid cache type: 'redi'
```

**Solution:**
```env
# In .env, use valid values:
CACHE_TYPE=memory  # or "redis", not "redi"
```

---

## API Issues

### Error: "Connection refused" to PokeAPI

**Symptom:**
```
ExternalAPIError: Failed to connect to PokeAPI
```

**Cause:** PokeAPI unavailable or timeout too low.

**Solution:**
```bash
# 1. Verify connectivity
ping pokeapi.co
curl https://pokeapi.co/api/v2/pokemon/pikachu

# 2. Increase timeout in .env
POKEAPI_TIMEOUT=30.0

# 3. Verify proxy (if applicable)
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 4. Disable proxy temporarily
unset HTTP_PROXY
unset HTTPS_PROXY
```

---

### Error: Port 8000 in Use

**Symptom:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Option 1: Use different port
uvicorn main:app --port 8001 --reload

# Option 2: Find and kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Option 3: Restart system (last resort)
```

---

### Error: "404 Not Found" on Endpoints

**Symptom:**
```json
{
  "detail": "Not Found"
}
```

**Cause:** Incorrect URL or endpoint does not exist.

**Solution:**
```bash
# 1. Verify correct URL
# Correct:
GET http://localhost:8000/pokemon/pikachu

# Incorrect:
GET http://localhost:8000/pokemons/pikachu  # Missing 's'

# 2. View available endpoints
curl http://localhost:8000/docs

# 3. Verify server is running
curl http://localhost:8000/health
```

---

### Error: "429 Too Many Requests"

**Symptom:**
```json
{
  "error": "RateLimitError",
  "message": "Too many requests"
}
```

**Solution:**
```bash
# 1. Wait 60 seconds

# 2. Disable rate limiting (development only)
# In .env:
RATE_LIMIT_ENABLED=false

# 3. Increase limit
RATE_LIMIT_MAX_REQUESTS=200
```

---

## Cache Errors

### Error: Redis Connection Failed

**Symptom:**
```
CacheError: Failed to connect to Redis
```

**Cause:** Redis is not running.

**Solution:**
```bash
# 1. Verify Redis
redis-cli ping
# Should respond: PONG

# 2. If no response, start Redis
# Linux:
sudo systemctl start redis

# Mac:
brew services start redis

# Windows (with Docker):
docker run -d -p 6379:6379 redis

# 3. Or switch to memory cache
# In .env:
CACHE_TYPE=memory
```

---

### Error: Cache Keys Do Not Exist

**Symptom:**
```python
cache.get("key") returns None  # Expected a value
```

**Cause:** TTL expired or cache cleared.

**Solution:**
```python
# Verify TTL
await cache.set("key", "value", ttl=3600)  # 1 hour

# Verify cache was not cleared unintentionally
await cache.clear()  # DO NOT do this accidentally
```

---

## AI Agent Issues

### Error: Agent Does Not Respond

**Symptom:**
```
Timeout waiting for agent response
```

**Cause:** Invalid API key or quota exceeded.

**Solution:**
```bash
# 1. Verify API key
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models

# 2. Check quota in Google AI Studio
# https://makersuite.google.com/app/usage

# 3. Wait if quota exceeded (renews daily)
```

---

### Error: Tool Execution Failed

**Symptom:**
```
AgentError: Failed to execute tool 'recommend_team_for_battle'
```

**Cause:** Error in tool or invalid parameters.

**Solution:**
```python
# 1. View detailed logs
python pokemon_strategy_cli.py --verbose

# 2. Test tool directly
from agent.tools import recommend_team_for_battle
result = await recommend_team_for_battle(
    available_pokemon=["pikachu"],
    opponent_types=["water"],
    team_size=1
)
```

---

## Testing Errors

### Error: Tests Failing After Changes

**Symptom:**
```
FAILED tests/test_pokemon_service.py::test_get_pokemon
```

**Cause:** Code changed but tests not updated.

**Solution:**
```bash
# 1. View failure details
pytest tests/test_pokemon_service.py::test_get_pokemon -vv

# 2. Update tests to reflect changes

# 3. Verify mocks
# Ensure mocks match new interfaces
```

---

### Error: "asyncio RuntimeError"

**Symptom:**
```
RuntimeError: Event loop is closed
```

**Cause:** Incorrect pytest-asyncio configuration.

**Solution:**
```ini
# In pytest.ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

---

### Error: Import Errors in Tests

**Symptom:**
```
ImportError: cannot import name 'ValidationError'
```

**Solution:**
```python
# Verify imports
from core.exceptions import ValidationError  # Correct

# Verify pythonpath in pytest.ini
[pytest]
pythonpath = .
```

---

## Performance Issues

### Issue: Slow Requests

**Symptom:** Requests take >5 seconds.

**Diagnosis:**
```bash
# 1. View logs with timestamps
uvicorn main:app --log-level debug

# 2. Verify cache
curl http://localhost:8000/cache/stats

# 3. Verify connection to PokeAPI
time curl https://pokeapi.co/api/v2/pokemon/pikachu
```

**Solution:**
```env
# Enable cache
CACHE_ENABLED=true
CACHE_TYPE=redis  # Faster than memory
CACHE_TTL=7200

# Increase timeout if network is slow
POKEAPI_TIMEOUT=20.0
```

---

### Issue: High Memory Usage

**Symptom:** Process uses >1GB RAM.

**Diagnosis:**
```bash
# Linux/Mac
top -p $(pgrep -f uvicorn)

# Windows
tasklist | findstr python
```

**Solution:**
```python
# Clear cache periodically
# In infrastructure/memory_cache.py
# Reduce cleanup interval
self._cleanup_interval = 60  # 1 minute instead of 5
```

---

## Logs and Debugging

### Enable Detailed Logs

```bash
# Uvicorn with debug logs
uvicorn main:app --log-level debug

# View HTTP requests
uvicorn main:app --access-log

# View errors only
uvicorn main:app --log-level error
```

---

### Debugging with Print

```python
# In any part of the code
import sys
print(f"DEBUG: variable = {variable}", file=sys.stderr)

# Or use logging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Value: {value}")
```

---

### Debugging with PDB

```python
# Add breakpoint
def some_function():
    result = process()
    
    import pdb; pdb.set_trace()  # STOPS HERE
    
    return result

# Useful commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code
# q - quit
```

---

### Review Uvicorn Logs

```bash
# Logs are written to stdout/stderr
# Redirect to file:
uvicorn main:app --reload > app.log 2>&1

# View in real time:
tail -f app.log

# Search for errors:
grep "ERROR" app.log
```

---

## Diagnostic Tools

### Diagnostic Script

```python
# diagnostic.py
import asyncio
from core.config import Settings
from core.dependencies import get_pokemon_repository

async def diagnose():
    """Run diagnostic checks."""
    print("Running diagnostics...\n")
    
    # 1. Config
    print("1. Configuration:")
    try:
        settings = Settings()
        print(f"   Config loaded")
        print(f"   - Cache: {settings.CACHE_TYPE}")
        print(f"   - Debug: {settings.DEBUG}")
    except Exception as e:
        print(f"   Config error: {e}")
    
    # 2. Repository
    print("\n2. Repository:")
    try:
        repo = await anext(get_pokemon_repository())
        result = await repo.get_pokemon("pikachu")
        print(f"   Can fetch Pokemon")
        print(f"   - Got: {result['name']}")
    except Exception as e:
        print(f"   Repository error: {e}")
    
    # 3. Cache
    print("\n3. Cache:")
    try:
        from core.dependencies import get_cache
        cache = await anext(get_cache())
        await cache.set("test", "value", ttl=60)
        value = await cache.get("test")
        if value == "value":
            print(f"   Cache working")
        else:
            print(f"   Cache not persisting")
    except Exception as e:
        print(f"   Cache error: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
```

**Usage:**
```bash
python diagnostic.py
```

---

## Getting Help

### Steps to Report a Bug

1. **Reproduce the error:**
   ```bash
   # Note exact steps
   python pokemon_strategy_cli.py
   # Select option 1
   # Input: pikachu, charizard
   # Error: ...
   ```

2. **Capture logs:**
   ```bash
   uvicorn main:app --log-level debug > debug.log 2>&1
   ```

3. **System information:**
   ```bash
   python --version
   pip list
   uname -a  # or systeminfo on Windows
   ```

4. **Create GitHub Issue** with:
   - Problem description
   - Steps to reproduce
   - Relevant logs
   - Python version and dependencies

---

### Support Channels

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For general questions
- **Documentation:** [Docs/README.md](./README.md)

---

## Resolution Checklist

Before reporting an issue, verify:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list`)
- [ ] .env file configured
- [ ] GOOGLE_API_KEY valid
- [ ] Port 8000 available
- [ ] Redis running (if using Redis cache)
- [ ] Tests passing (`pytest tests/`)
- [ ] Server started (`uvicorn main:app`)

---

Most issues are resolved by restarting the server or verifying configuration.
