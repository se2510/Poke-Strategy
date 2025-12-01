# Scripts - Pokemon Strategy Agent

Essential utility scripts for the Pokemon Strategy Agent project.

## Available Scripts (3 files)

### 1. pokemon_strategy_cli.py

**Interactive CLI application** - Main user interface for the Pokemon Strategy Agent.

```bash
python scripts/pokemon_strategy_cli.py
```

**Features:**
- Interactive menu with 6 options
- All 4 use cases implemented
- Toggle between ADK Agent and Direct Client (option 6)
- User-friendly prompts and error handling
- Real-time response generation

**Menu Options:**
```
[1] Recommended Team for Combat
[2] Group and Classify Pokemon
[3] Most Complete Generation
[4] Personality Test - Discover Your Pokemon
[5] Custom Question
[6] Toggle Agent Implementation
[0] Exit
```

---

### 2. test_agent_comparison.py

**Compare ADK Agent vs Direct Gemini Client** - Benchmark both implementations.

```bash
# Full comparison suite
python scripts/test_agent_comparison.py

# Quick test
python scripts/test_agent_comparison.py --quick
```

**Tests:**
- Response quality
- Performance benchmarks
- Cache behavior
- Tool calling accuracy

---

### 3. quick_personality_test.py

**Quick personality test demo** - Standalone script for rapid testing.

```bash
python scripts/quick_personality_test.py
```

**Features:**
- Predefined profiles
- Direct API testing
- Fast validation

---

## Quick Start

```bash
# 1. Navigate and activate venv
cd backend
venv\Scripts\activate  # Windows

# 2. Start API server (separate terminal)
uvicorn main:app --reload

# 3. Run main CLI
python scripts/pokemon_strategy_cli.py
```

---

## Troubleshooting

### API Server Required

```bash
# Terminal 1: API Server
uvicorn main:app --reload

# Terminal 2: Scripts
python scripts/pokemon_strategy_cli.py
```

### Missing API Key

```bash
# Create .env file
cp .env.example .env
# Add: GOOGLE_API_KEY=your-key-here
```

---

## Documentation

- `Docs/OUTPUT_EXAMPLES.md` - Example outputs
- `Docs/PERSONALITY_TEST_GUIDE.md` - Personality feature guide
- `Docs/13-ADK-AGENT-IMPLEMENTATION.md` - Agent comparison

---

## Cleanup History

**Removed (redundant):**
- test_real_time.py
- test_personality_feature.py
- examples_usage.py

**Moved to Docs/:**
- OUTPUT_EXAMPLES.md
- PERSONALITY_TEST_GUIDE.md

---

**Status**: Clean and Professional  
**Version**: 1.0.0
