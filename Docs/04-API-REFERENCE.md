# REST API Reference

Complete documentation of all endpoints available in the Pokémon Strategy Agent REST API.

## Base URL

```
http://localhost:8000
```

**Interactive Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoint Index

### System Information
- [GET /](#get-) - Root endpoint
- [GET /health](#get-health) - Health check

### Basic Pokemon
- [GET /pokemon/](#get-pokemon) - List Pokemon
- [GET /pokemon/{name}](#get-pokemonname) - Get specific Pokemon
- [GET /pokemon/{name}/summary](#get-pokemonnamesummary) - Compact summary
- [GET /pokemon/{name}/with-abilities](#get-pokemonnamewith-abilities) - With detailed abilities

### Types and Comparison
- [GET /pokemon/type/{type_name}/summary](#get-pokemontypetype_namesummary) - Type summary
- [GET /pokemon/compare](#get-pokemoncompare) - Compare two Pokemon

### Team Analysis
- [POST /pokemon/team/recommend](#post-pokemonteamrecommend) - Recommend team
- [POST /pokemon/team/strength](#post-pokemonteamstrength) - Calculate strength

### Grouping and Classification
- [POST /pokemon/group/by-type](#post-pokemongroupby-type) - Group by type
- [POST /pokemon/classify/by-role](#post-pokemonclassifyby-role) - Classify by role

### Generations
- [GET /pokemon/generation/compare](#get-pokemongenerationcompare) - Compare generations

### Personality Analysis
- [POST /pokemon/personality/analyze](#post-pokemonpersonalityanalyze) - Analyze personality from preferences
- [POST /pokemon/personality/analyze-from-text](#post-pokemonpersonalityanalyze-from-text) - Analyze personality from text

### Utilities
- [GET /cache/stats](#get-cachestats) - Cache statistics
- [GET /rate/status](#get-ratestatus) - Rate limiting status

## Detailed Endpoints

### GET /

**Description:** Root endpoint with API information.

**Request:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "message": "Pokemon Strategy API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### GET /health

**Description:** Service health check.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200` - Service healthy
- `503` - Service degraded

### GET /pokemon/

**Description:** Lists Pokemon with pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Number of results (1-100) |
| `offset` | int | 0 | Starting index |

**Request:**
```http
GET /pokemon/?limit=5&offset=0 HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "count": 1302,
  "next": "https://pokeapi.co/api/v2/pokemon?offset=5&limit=5",
  "previous": null,
  "results": [
    {
      "name": "bulbasaur",
      "url": "https://pokeapi.co/api/v2/pokemon/1/"
    },
    {
      "name": "ivysaur",
      "url": "https://pokeapi.co/api/v2/pokemon/2/"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters
- `429` - Rate limit exceeded

### GET /pokemon/{name}

**Description:** Retrieves complete Pokemon information.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Pokemon name or ID |

**Request:**
```http
GET /pokemon/pikachu HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "id": 25,
  "name": "pikachu",
  "height": 4,
  "weight": 60,
  "base_experience": 112,
  "types": [
    {
      "slot": 1,
      "type": {
        "name": "electric",
        "url": "https://pokeapi.co/api/v2/type/13/"
      }
    }
  ],
  "stats": [
    {
      "base_stat": 35,
      "effort": 0,
      "stat": {
        "name": "hp"
      }
    },
    {
      "base_stat": 55,
      "effort": 0,
      "stat": {
        "name": "attack"
      }
    }
  ],
  "abilities": [...],
  "moves": [...],
  "sprites": {...}
}
```

**Status Codes:**
- `200` - Pokemon found
- `400` - Invalid name
- `404` - Pokemon not found
- `502` - PokeAPI error

### GET /pokemon/{name}/summary

**Description:** Compact Pokemon summary (optimized for LLMs).

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Pokemon name |

**Request:**
```http
GET /pokemon/pikachu/summary HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "id": 25,
  "name": "pikachu",
  "height": 4,
  "weight": 60,
  "base_experience": 112,
  "types": ["electric"],
  "abilities": ["static", "lightning-rod"],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special-attack": 50,
    "special-defense": 50,
    "speed": 90
  },
  "moves_sample": ["thunder-shock", "growl", "tail-whip"],
  "moves_count": 98,
  "sprite": "https://raw.githubusercontent.com/.../pikachu.png"
}
```

**Features:**
- Essential data only
- Types as simple strings
- Stats in dictionary format
- Move sample (max 10)

### GET /pokemon/{name}/with-abilities

**Description:** Pokemon with detailed ability information.

**Request:**
```http
GET /pokemon/pikachu/with-abilities HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "id": 25,
  "name": "pikachu",
  "types": ["electric"],
  "abilities_details": [
    {
      "name": "static",
      "effect": "May paralyze opponents on contact",
      "short_effect": "30% chance to paralyze on contact"
    },
    {
      "name": "lightning-rod",
      "effect": "Draws in Electric-type moves",
      "short_effect": "Absorbs Electric moves"
    }
  ]
}
```

### GET /pokemon/type/{type_name}/summary

**Description:** Summary of Pokemon by type.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type_name` | string | Type name (fire, water, etc.) |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Maximum Pokemon (1-50) |

**Request:**
```http
GET /pokemon/type/electric/summary?limit=5 HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "type": "electric",
  "total_available": 76,
  "returned": 5,
  "pokemons": [
    {
      "id": 25,
      "name": "pikachu",
      "types": ["electric"],
      "stats": {...}
    },
    {
      "id": 26,
      "name": "raichu",
      "types": ["electric"],
      "stats": {...}
    }
  ]
}
```

### GET /pokemon/compare

**Description:** Compares two Pokemon.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `first` | string | First Pokemon name |
| `second` | string | Second Pokemon name |

**Request:**
```http
GET /pokemon/compare?first=pikachu&second=raichu HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "first": {
    "id": 25,
    "name": "pikachu",
    "types": ["electric"],
    "stats": {...}
  },
  "second": {
    "id": 26,
    "name": "raichu",
    "types": ["electric"],
    "stats": {...}
  },
  "comparison": {
    "higher_attack": "raichu",
    "higher_defense": "raichu",
    "higher_hp": "raichu",
    "higher_speed": "raichu",
    "types_overlap": ["electric"]
  }
}
```

### POST /pokemon/team/recommend

**Description:** Recommends optimal team for battle.

**Request Body:**
```json
{
  "available_pokemon": ["pikachu", "charizard", "blastoise", "venusaur", "gengar", "alakazam"],
  "opponent_types": ["water", "rock"],
  "team_size": 3
}
```

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| `available_pokemon` | string[] | Available Pokemon for selection |
| `opponent_types` | string[] \| null | Expected opponent types (optional) |
| `team_size` | int | Team size (1-6) |

**Request:**
```http
POST /pokemon/team/recommend HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "available_pokemon": ["pikachu", "charizard", "blastoise"],
  "opponent_types": ["water"],
  "team_size": 2
}
```

**Response:**
```json
{
  "recommended_team": [
    {
      "name": "pikachu",
      "score": 450,
      "reason": "Type advantage against Water"
    },
    {
      "name": "venusaur",
      "score": 425,
      "reason": "Grass type effective against Water"
    }
  ],
  "team_stats": {
    "total_score": 875,
    "average_stats": 425,
    "type_coverage": ["electric", "grass", "poison"]
  },
  "explanation": "This team has excellent coverage against Water types..."
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters (empty list, invalid team_size)

### POST /pokemon/team/strength

**Description:** Calculates team strength and synergies.

**Request Body:**
```json
{
  "pokemon_names": ["pikachu", "charizard", "blastoise"]
}
```

**Response:**
```json
{
  "team": ["pikachu", "charizard", "blastoise"],
  "team_size": 3,
  "type_coverage": ["electric", "fire", "flying", "water"],
  "type_distribution": {
    "electric": 1,
    "fire": 1,
    "water": 1,
    "flying": 1
  },
  "average_stats": {
    "hp": 66.67,
    "attack": 70.33,
    "defense": 65.00,
    "speed": 78.33
  },
  "role_distribution": {
    "attacker": 2,
    "balanced": 1
  },
  "strengths": [
    "Excellent type diversity",
    "Strong offensive capabilities"
  ],
  "recommendations": [
    "Consider adding a defensive Pokemon",
    "Watch out for Electric weakness (Blastoise, Charizard)"
  ]
}
```

### POST /pokemon/group/by-type

**Description:** Groups Pokemon by primary type.

**Request Body:**
```json
{
  "pokemon_names": ["pikachu", "charmander", "squirtle", "bulbasaur", "raichu"]
}
```

**Response:**
```json
{
  "groups": {
    "electric": [
      {"name": "pikachu", "types": ["electric"]},
      {"name": "raichu", "types": ["electric"]}
    ],
    "fire": [
      {"name": "charmander", "types": ["fire"]}
    ],
    "water": [
      {"name": "squirtle", "types": ["water"]}
    ],
    "grass": [
      {"name": "bulbasaur", "types": ["grass", "poison"]}
    ]
  },
  "markdown": "# Pokemon Grouped by Type\n\n## Electric (2)\n- pikachu\n- raichu\n\n## Fire (1)\n- charmander\n...",
  "total_pokemons": 5,
  "type_count": 4
}
```

### POST /pokemon/classify/by-role

**Description:** Classifies Pokemon by battle role based on stats.

**Request Body:**
```json
{
  "pokemon_names": ["mewtwo", "blissey", "alakazam", "snorlax"]
}
```

**Response:**
```json
{
  "roles": {
    "attacker": ["mewtwo", "alakazam"],
    "tank": ["blissey"],
    "balanced": ["snorlax"]
  },
  "markdown": "# Pokemon Classification by Role\n\n## Attacker (2)\n...",
  "total_classified": 4
}
```

**Roles:**
- **Attacker:** High Attack or Special Attack
- **Tank:** High HP and Defense
- **Fast:** High Speed
- **Balanced:** Balanced stats

### GET /pokemon/generation/compare

**Description:** Compares Pokemon generations.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `generation_ids` | string[] | Generation IDs (e.g., ["1", "2"]) |
| `criteria` | string | Criteria: "variety", "stats", "count" |

**Request:**
```http
GET /pokemon/generation/compare?generation_ids=1&generation_ids=2&criteria=variety HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "generations": [
    {
      "generation": "1",
      "name": "generation-i",
      "total_pokemon": 151,
      "type_diversity": 15,
      "average_total_stats": 432.5,
      "main_region": "kanto"
    },
    {
      "generation": "2",
      "name": "generation-ii",
      "total_pokemon": 100,
      "type_diversity": 15,
      "average_total_stats": 428.3,
      "main_region": "johto"
    }
  ],
  "winner": {
    "generation": "1",
    "score": 151
  },
  "markdown": "# Generation Comparison...",
  "criteria": "variety"
}
```

### POST /pokemon/personality/analyze

**Description:** Analyzes personality based on Pokemon starter preferences.

Analyzes all official starter Pokemon (Generations I-IX) and determines personality based on battle style, preferred stat, and element preference.

**Personality Mapping:**
- High HP → Resilient, Patient, Enduring
- High Attack → Assertive, Direct, Competitive
- High Defense → Cautious, Protective, Strategic
- High Special Attack → Creative, Intellectual, Innovative
- High Special Defense → Composed, Stable, Thoughtful
- High Speed → Energetic, Adaptable, Quick-thinking

**Request Body:**
```json
{
  "battle_style": "aggressive",
  "preferred_stat": "speed",
  "element_preference": "fire"
}
```

**Field Descriptions:**
| Field | Type | Valid Values | Description |
|-------|------|--------------|-------------|
| `battle_style` | string | aggressive, defensive, balanced, tactical | Approach to challenges |
| `preferred_stat` | string | hp, attack, defense, special-attack, special-defense, speed | Most valued stat |
| `element_preference` | string | fire, water, grass, any | Preferred element |

**Request:**
```http
POST /pokemon/personality/analyze HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "battle_style": "aggressive",
  "preferred_stat": "speed",
  "element_preference": "fire"
}
```

**Response:**
```json
{
  "matched_starter": "charmander",
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
      "description": "Adapts quickly to change and thinks on feet"
    },
    {
      "stat": "Special Attack",
      "value": 60,
      "traits": ["Creative", "Intellectual", "Innovative", "Visionary"],
      "description": "Approaches challenges with unique and creative solutions"
    },
    {
      "stat": "Attack",
      "value": 52,
      "traits": ["Assertive", "Direct", "Competitive", "Bold"],
      "description": "Tackles problems head-on with confidence and determination"
    }
  ],
  "match_score": 387.5,
  "alternative_matches": [
    {"name": "torchic", "score": 365.0},
    {"name": "chimchar", "score": 358.5},
    {"name": "fennekin", "score": 352.0}
  ],
  "summary": "# Your Pokemon Personality: Charmander\n\n**Type**: Fire\n**Generation**: I (Kanto)\n\n..."
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters

### POST /pokemon/personality/analyze-from-text

**Description:** Analyzes personality from natural language text.

Uses AI to interpret free-form text describing personality, preferences, or challenge approaches, then extracts preferences and matches with a Pokemon starter.

**Request Body:**
```json
{
  "user_text": "I'm very competitive and always rush into challenges. I love the thrill of action!"
}
```

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| `user_text` | string | Free-form text describing personality or preferences |

**Example Texts:**
- "I'm very competitive and always rush into challenges. I love the thrill of action!"
- "I prefer to think things through carefully and protect what's important to me."
- "I value creativity and finding unique solutions. I'm passionate and energetic."
- "I'm adaptable and balanced, I can handle any situation that comes my way."

**Request:**
```http
POST /pokemon/personality/analyze-from-text HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "user_text": "I'm very competitive and always rush into challenges. I love action!"
}
```

**Response:**
```json
{
  "matched_starter": "torchic",
  "starter_details": {...},
  "personality_traits": [...],
  "trait_analysis": [...],
  "match_score": 425.0,
  "alternative_matches": [...],
  "summary": "...",
  "interpretation": {
    "original_text": "I'm very competitive and always rush into challenges. I love action!",
    "extracted_preferences": {
      "battle_style": "aggressive",
      "preferred_stat": "attack",
      "element_preference": "fire"
    },
    "confidence": "high",
    "reasoning": "Text indicates aggressive approach with focus on action and competition"
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid or empty text

### GET /cache/stats

**Description:** Cache statistics.

**Response:**
```json
{
  "type": "memory",
  "size": 42,
  "status": "active"
}
```

### GET /rate/status

**Description:** Rate limiting status.

**Response:**
```json
{
  "enabled": true,
  "max_requests": 100,
  "window_seconds": 60,
  "remaining": 87
}
```

## Rate Limiting

**Default limits:**
- 100 requests per minute per IP
- Response headers:
  - `X-RateLimit-Limit`: Maximum limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

**Response when exceeded:**
```json
{
  "error": "RateLimitError",
  "message": "Too many requests",
  "retry_after": 45
}
```

**Status Code:** `429 Too Many Requests`

## Error Handling

### Standard Error Format

```json
{
  "error": "ValidationError",
  "message": "Pokemon name cannot be empty",
  "field": "name",
  "value": ""
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Pokemon not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 502 | Bad Gateway | PokeAPI error |
| 503 | Service Unavailable | Service down |

### Error Types

```python
# ValidationError (400)
{
  "error": "ValidationError",
  "message": "Limit must be between 1 and 100",
  "field": "limit",
  "value": 150
}

# ResourceNotFoundError (404)
{
  "error": "ResourceNotFoundError",
  "message": "Pokemon not found",
  "resource": "pokemon",
  "identifier": "unknown-pokemon"
}

# ExternalAPIError (502)
{
  "error": "ExternalAPIError",
  "message": "PokeAPI is currently unavailable",
  "service": "pokeapi"
}
```

## Usage Examples

### cURL

```bash
# List Pokemon
curl "http://localhost:8000/pokemon/?limit=5"

# Get Pikachu
curl "http://localhost:8000/pokemon/pikachu"

# Recommend team
curl -X POST "http://localhost:8000/pokemon/team/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "available_pokemon": ["pikachu", "charizard", "blastoise"],
    "opponent_types": ["water"],
    "team_size": 2
  }'

# Analyze personality from preferences
curl -X POST "http://localhost:8000/pokemon/personality/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "battle_style": "aggressive",
    "preferred_stat": "speed",
    "element_preference": "fire"
  }'

# Analyze personality from text
curl -X POST "http://localhost:8000/pokemon/personality/analyze-from-text" \
  -H "Content-Type: application/json" \
  -d '{
    "user_text": "I love competition and rushing into action!"
  }'
```

### Python (httpx)

```python
import httpx

async def get_pokemon(name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/pokemon/{name}")
        return response.json()

async def analyze_personality(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/pokemon/personality/analyze-from-text",
            json={"user_text": text}
        )
        return response.json()

# Usage
data = await get_pokemon("pikachu")
personality = await analyze_personality("I'm competitive and energetic!")
```

### JavaScript (fetch)

```javascript
// Get Pokemon
const response = await fetch('http://localhost:8000/pokemon/pikachu');
const data = await response.json();

// Recommend team
const teamResponse = await fetch('http://localhost:8000/pokemon/team/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    available_pokemon: ['pikachu', 'charizard', 'blastoise'],
    opponent_types: ['water'],
    team_size: 2
  })
});
const team = await teamResponse.json();

// Analyze personality
const personalityResponse = await fetch('http://localhost:8000/pokemon/personality/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    battle_style: 'aggressive',
    preferred_stat: 'speed',
    element_preference: 'fire'
  })
});
const personality = await personalityResponse.json();
```

## Configuration

For customization options, see the configuration guide:
- Timeouts
- Cache settings
- Rate limiting
- Logging

**Automatic documentation generated by FastAPI: http://localhost:8000/docs**
