"""
Personality Test Domain Models

Data models for the personality test feature following domain-driven design.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class BattleStyle(str, Enum):
    """Battle style preferences."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    TACTICAL = "tactical"


class PreferredStat(str, Enum):
    """Preferred Pokemon statistics."""
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special-attack"
    SPECIAL_DEFENSE = "special-defense"
    SPEED = "speed"


class ElementPreference(str, Enum):
    """Element type preferences."""
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ANY = "any"


@dataclass
class PersonalityPreferences:
    """User personality preferences for matching."""
    battle_style: BattleStyle
    preferred_stat: PreferredStat
    element_preference: ElementPreference
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API calls."""
        return {
            "battle_style": self.battle_style.value,
            "preferred_stat": self.preferred_stat.value,
            "element_preference": self.element_preference.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PersonalityPreferences':
        """Create from dictionary."""
        return cls(
            battle_style=BattleStyle(data["battle_style"]),
            preferred_stat=PreferredStat(data["preferred_stat"]),
            element_preference=ElementPreference(data["element_preference"])
        )


@dataclass
class AlternativeMatch:
    """Alternative Pokemon match."""
    name: str
    score: int


@dataclass
class PersonalityResult:
    """Result of personality analysis."""
    matched_starter: str
    match_score: int
    personality_traits: List[str]
    alternative_matches: List[AlternativeMatch]
    summary: str
    stats_mapping: Optional[Dict[str, int]] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'PersonalityResult':
        """Create from API response."""
        alternatives = [
            AlternativeMatch(name=alt["name"], score=alt["score"])
            for alt in data.get("alternative_matches", [])
        ]
        
        return cls(
            matched_starter=data["matched_starter"],
            match_score=data["match_score"],
            personality_traits=data["personality_traits"],
            alternative_matches=alternatives,
            summary=data.get("summary", ""),
            stats_mapping=data.get("stats_mapping")
        )


@dataclass
class TextInterpretation:
    """AI interpretation of user text."""
    original_text: str
    extracted_preferences: PersonalityPreferences
    confidence: str
    reasoning: str


@dataclass
class TextAnalysisResult(PersonalityResult):
    """Result including text interpretation."""
    interpretation: Optional[TextInterpretation] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'TextAnalysisResult':
        """Create from API response with interpretation."""
        base_result = PersonalityResult.from_api_response(data)
        
        interp_data = data.get("interpretation", {})
        interpretation = TextInterpretation(
            original_text=interp_data.get("original_text", ""),
            extracted_preferences=PersonalityPreferences.from_dict(
                interp_data.get("extracted_preferences", {})
            ),
            confidence=interp_data.get("confidence", "medium"),
            reasoning=interp_data.get("reasoning", "")
        )
        
        return cls(
            matched_starter=base_result.matched_starter,
            match_score=base_result.match_score,
            personality_traits=base_result.personality_traits,
            alternative_matches=base_result.alternative_matches,
            summary=base_result.summary,
            stats_mapping=base_result.stats_mapping,
            interpretation=interpretation
        )


@dataclass
class QuizQuestion:
    """Question for the personality quiz."""
    number: int
    title: str
    description: str
    options: Dict[str, tuple[str, str]]  # key -> (value, description)
    
    def display(self) -> None:
        """Display question to user."""
        print(f"\nQuestion {self.number}: {self.title}")
        for key, (_, desc) in self.options.items():
            print(f"  {key}. {desc}")
        print()


@dataclass
class DemoProfile:
    """Predefined personality profile for demos."""
    name: str
    description: str
    preferences: PersonalityPreferences
