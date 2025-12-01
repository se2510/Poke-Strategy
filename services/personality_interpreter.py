"""
Personality Interpreter Service

Interprets free-form user text to extract personality preferences
for Pokemon starter matching using Google Gemini with keyword fallback.
"""

from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch
from typing import Dict, Any, Optional
from core.config import get_settings
from core.exceptions import ValidationError
import re


class PersonalityInterpreter:
    """Interprets natural language to extract personality preferences."""
    
    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_id = 'gemini-2.0-flash-exp'
        
        # Keyword mappings for fallback analysis
        self.battle_style_keywords = {
            "aggressive": ["competitivo", "agresivo", "atrevido", "lanzado", "directo", "audaz", 
                          "competitive", "aggressive", "bold", "daring", "direct", "forceful",
                          "rush", "attack", "fight", "primero", "first", "rápido"],
            "defensive": ["cauteloso", "protector", "paciente", "cuidadoso", "defensivo",
                         "cautious", "protective", "patient", "careful", "defensive",
                         "shield", "guard", "safe", "seguro", "proteger"],
            "tactical": ["estratégico", "inteligente", "creativo", "analítico", "pensativo",
                        "strategic", "smart", "creative", "analytical", "tactical",
                        "plan", "think", "strategy", "clever", "ingenioso"],
            "balanced": ["equilibrado", "adaptable", "versátil", "moderado", "flexible",
                        "balanced", "adaptable", "versatile", "moderate", "flexible",
                        "any", "situación", "situation", "varies"]
        }
        
        self.stat_keywords = {
            "attack": ["fuerte", "poder", "ataque", "fuerza", "poderoso", "golpe",
                      "strong", "power", "attack", "strength", "powerful", "hit",
                      "agresivo", "aggressive", "directo", "direct"],
            "defense": ["resistente", "defensa", "proteger", "aguante", "duro",
                       "resistant", "defense", "protect", "endurance", "tough",
                       "shield", "wall", "seguro", "safe"],
            "special-attack": ["creativo", "especial", "único", "inteligente", "ingenioso",
                              "creative", "special", "unique", "smart", "clever",
                              "magic", "estrategia", "strategy"],
            "speed": ["rápido", "veloz", "ágil", "primero", "ligero", "veloz",
                     "fast", "quick", "agile", "first", "light", "swift",
                     "lanzado", "energético", "energetic"],
            "hp": ["resistencia", "aguante", "duradero", "perseverante", "constante",
                  "endurance", "stamina", "durable", "persistent", "lasting"],
            "special-defense": ["calmado", "tranquilo", "sabio", "sereno", "compostura",
                               "calm", "tranquil", "wise", "serene", "composed"]
        }
        
        self.element_keywords = {
            "fire": ["pasión", "energía", "calor", "intenso", "entusiasmo", "fuego",
                    "passion", "energy", "heat", "intense", "enthusiasm", "fire"],
            "water": ["fluir", "adaptable", "fluido", "calma", "agua", "profundo",
                     "flow", "adaptable", "fluid", "calm", "water", "deep"],
            "grass": ["crecimiento", "naturaleza", "armonía", "balance", "nutrir",
                     "growth", "nature", "harmony", "balance", "nurture", "plant"]
        }
    
    def _fallback_keyword_analysis(self, user_text: str) -> Dict[str, str]:
        """Analyze text using keyword matching when AI is unavailable."""
        text_lower = user_text.lower()
        
        # Analyze battle style
        battle_scores = {style: 0 for style in self.battle_style_keywords}
        for style, keywords in self.battle_style_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    battle_scores[style] += 1
        
        battle_style = max(battle_scores, key=battle_scores.get)
        if battle_scores[battle_style] == 0:
            battle_style = "balanced"
        
        # Analyze preferred stat
        stat_scores = {stat: 0 for stat in self.stat_keywords}
        for stat, keywords in self.stat_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    stat_scores[stat] += 1
        
        preferred_stat = max(stat_scores, key=stat_scores.get)
        if stat_scores[preferred_stat] == 0:
            # Default based on battle style
            defaults = {
                "aggressive": "attack",
                "defensive": "defense",
                "tactical": "special-attack",
                "balanced": "speed"
            }
            preferred_stat = defaults.get(battle_style, "speed")
        
        # Analyze element preference
        element_scores = {elem: 0 for elem in self.element_keywords}
        for element, keywords in self.element_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    element_scores[element] += 1
        
        max_element_score = max(element_scores.values()) if element_scores else 0
        element_preference = max(element_scores, key=element_scores.get) if max_element_score > 0 else "any"
        
        return {
            "battle_style": battle_style,
            "preferred_stat": preferred_stat,
            "element_preference": element_preference,
            "confidence": "medium" if sum(battle_scores.values()) > 0 else "low",
            "reasoning": f"Análisis basado en palabras clave (fallback mode)"
        }
    
    async def interpret_user_text(self, user_text: str) -> Dict[str, str]:
        """Extract personality preferences from free-form text.
        
        Args:
            user_text: Natural language description from user
            
        Returns:
            Dictionary with battle_style, preferred_stat, element_preference
            
        Raises:
            ValidationError: If unable to extract preferences or text is invalid
        """
        if not user_text or not user_text.strip():
            raise ValidationError(
                message="User text cannot be empty",
                field="user_text",
                value=user_text
            )
        
        if len(user_text.strip()) < 10:
            raise ValidationError(
                message="User text too short. Please provide more detail about yourself.",
                field="user_text",
                value=user_text
            )
        
        # Create prompt for extraction
        extraction_prompt = f"""
You are a personality analyzer for a Pokemon personality quiz. 
Extract the following preferences from the user's text:

1. **battle_style**: How they approach challenges
   - "aggressive" if they: tackle problems head-on, are competitive, direct, forceful, bold
   - "defensive" if they: are cautious, protective, patient, steady, prepare carefully
   - "tactical" if they: use strategy, are creative, analytical, think outside the box
   - "balanced" if they: adapt to situations, are versatile, well-rounded, moderate

2. **preferred_stat**: What quality they value most
   - "hp" if they value: endurance, stamina, resilience, persistence, longevity
   - "attack" if they value: strength, power, directness, assertiveness, impact
   - "defense" if they value: protection, stability, safety, reliability, security
   - "special-attack" if they value: creativity, intelligence, innovation, uniqueness, wit
   - "special-defense" if they value: composure, emotional stability, calmness, wisdom, thoughtfulness
   - "speed" if they value: quickness, agility, adaptability, energy, dynamism

3. **element_preference**: Their affinity (if mentioned)
   - "fire" if they mention: passion, energy, heat, intensity, enthusiasm
   - "water" if they mention: flow, adaptability, fluidity, calmness, depth
   - "grass" if they mention: growth, nature, harmony, balance, nurturing
   - "any" if not specified or unclear

USER TEXT:
\"\"\"
{user_text}
\"\"\"

OUTPUT FORMAT (JSON only, no explanation):
{{
  "battle_style": "<aggressive|defensive|tactical|balanced>",
  "preferred_stat": "<hp|attack|defense|special-attack|special-defense|speed>",
  "element_preference": "<fire|water|grass|any>",
  "confidence": "<high|medium|low>",
  "reasoning": "<brief explanation of why these preferences were chosen>"
}}

IMPORTANT: 
- Choose the BEST match even if not explicitly stated
- Infer from context and personality descriptions
- Use "any" for element_preference if truly ambiguous
- Be decisive - don't use placeholders
"""
        
        try:
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=extraction_prompt
            )
            
            if not response or not response.text:
                # Fallback to keyword analysis
                return self._fallback_keyword_analysis(user_text)
            
            # Extract JSON from response
            import json
            
            # Try to find JSON in response
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*\n?', '', text)
                text = re.sub(r'\n?```\s*$', '', text)
            
            # Parse JSON
            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                # Try to extract JSON object from text
                match = re.search(r'\{[^}]+\}', text, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                else:
                    raise ValidationError(
                        message="Could not parse AI response. Please try different phrasing.",
                        field="user_text",
                        value=user_text
                    )
            
            # Validate extracted preferences
            valid_battle_styles = ["aggressive", "defensive", "balanced", "tactical"]
            valid_stats = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
            valid_elements = ["fire", "water", "grass", "any"]
            
            battle_style = result.get("battle_style", "").lower()
            preferred_stat = result.get("preferred_stat", "").lower()
            element_preference = result.get("element_preference", "").lower()
            
            if battle_style not in valid_battle_styles:
                raise ValidationError(
                    message=f"Invalid battle_style extracted: {battle_style}",
                    field="battle_style",
                    value=battle_style
                )
            
            if preferred_stat not in valid_stats:
                raise ValidationError(
                    message=f"Invalid preferred_stat extracted: {preferred_stat}",
                    field="preferred_stat",
                    value=preferred_stat
                )
            
            if element_preference not in valid_elements:
                raise ValidationError(
                    message=f"Invalid element_preference extracted: {element_preference}",
                    field="element_preference",
                    value=element_preference
                )
            
            return {
                "battle_style": battle_style,
                "preferred_stat": preferred_stat,
                "element_preference": element_preference,
                "confidence": result.get("confidence", "medium"),
                "reasoning": result.get("reasoning", "Extracted from user description")
            }
            
        except ValidationError:
            raise
        except Exception as e:
            # If Gemini API fails (quota, network, etc.), use fallback
            error_str = str(e).lower()
            if any(x in error_str for x in ['quota', '429', 'resource_exhausted', 'rate limit']):
                # Use keyword-based fallback
                return self._fallback_keyword_analysis(user_text)
            
            raise ValidationError(
                message=f"Error interpreting text: {str(e)}",
                field="user_text",
                value=user_text
            )


# Singleton instance
_interpreter_instance: Optional[PersonalityInterpreter] = None


def get_personality_interpreter() -> PersonalityInterpreter:
    """Get or create personality interpreter singleton."""
    global _interpreter_instance
    if _interpreter_instance is None:
        _interpreter_instance = PersonalityInterpreter()
    return _interpreter_instance
