"""
Personality Quiz UI Module

Handles user interaction for the personality quiz.
Separates presentation logic from business logic (Single Responsibility).
"""

from typing import Dict, Tuple, Optional
from core.personality_models import (
    BattleStyle,
    PreferredStat,
    ElementPreference,
    PersonalityPreferences,
    QuizQuestion,
    DemoProfile
)


class QuizQuestions:
    """Quiz questions configuration following Open/Closed principle."""
    
    BATTLE_STYLE = QuizQuestion(
        number=1,
        title="What's your approach to challenges?",
        description="How do you typically handle difficult situations?",
        options={
            "1": (BattleStyle.AGGRESSIVE.value, "Aggressive - I tackle problems head-on with force"),
            "2": (BattleStyle.DEFENSIVE.value, "Defensive - I protect and prepare carefully"),
            "3": (BattleStyle.BALANCED.value, "Balanced - I adapt to the situation"),
            "4": (BattleStyle.TACTICAL.value, "Tactical - I use strategy and creativity")
        }
    )
    
    PREFERRED_STAT = QuizQuestion(
        number=2,
        title="What quality do you value most?",
        description="Which characteristic is most important to you?",
        options={
            "1": (PreferredStat.HP.value, "HP (Resilience) - Endurance and stamina"),
            "2": (PreferredStat.ATTACK.value, "Attack (Power) - Direct strength and force"),
            "3": (PreferredStat.DEFENSE.value, "Defense (Protection) - Safety and stability"),
            "4": (PreferredStat.SPECIAL_ATTACK.value, "Special Attack (Creativity) - Innovation and intelligence"),
            "5": (PreferredStat.SPECIAL_DEFENSE.value, "Special Defense (Composure) - Emotional stability"),
            "6": (PreferredStat.SPEED.value, "Speed (Agility) - Quick thinking and adaptability")
        }
    )
    
    ELEMENT_PREFERENCE = QuizQuestion(
        number=3,
        title="Which element resonates with you?",
        description="What type of energy appeals to you?",
        options={
            "1": (ElementPreference.FIRE.value, "Fire - Passion and energy"),
            "2": (ElementPreference.WATER.value, "Water - Fluidity and adaptability"),
            "3": (ElementPreference.GRASS.value, "Grass - Growth and harmony"),
            "4": (ElementPreference.ANY.value, "Any - I'm open to all")
        }
    )


class DemoProfiles:
    """Predefined demo profiles for quick testing."""
    
    PROFILES = [
        DemoProfile(
            name="The Aggressive Speedster",
            description="Fast and fierce, tackles challenges head-on",
            preferences=PersonalityPreferences(
                battle_style=BattleStyle.AGGRESSIVE,
                preferred_stat=PreferredStat.SPEED,
                element_preference=ElementPreference.FIRE
            )
        ),
        DemoProfile(
            name="The Defensive Tank",
            description="Patient and protective, values endurance",
            preferences=PersonalityPreferences(
                battle_style=BattleStyle.DEFENSIVE,
                preferred_stat=PreferredStat.HP,
                element_preference=ElementPreference.WATER
            )
        ),
        DemoProfile(
            name="The Tactical Strategist",
            description="Creative and intelligent, uses strategy over force",
            preferences=PersonalityPreferences(
                battle_style=BattleStyle.TACTICAL,
                preferred_stat=PreferredStat.SPECIAL_ATTACK,
                element_preference=ElementPreference.GRASS
            )
        ),
        DemoProfile(
            name="The Balanced Warrior",
            description="Well-rounded and adaptable to any situation",
            preferences=PersonalityPreferences(
                battle_style=BattleStyle.BALANCED,
                preferred_stat=PreferredStat.ATTACK,
                element_preference=ElementPreference.ANY
            )
        )
    ]


class QuizInputHandler:
    """Handles user input validation for the quiz."""
    
    @staticmethod
    def get_choice(
        question: QuizQuestion,
        retry_message: str = "[ERROR] Invalid choice. Please try again."
    ) -> Tuple[str, str]:
        """
        Get valid user choice for a question.
        
        Args:
            question: QuizQuestion to ask
            retry_message: Message to show on invalid input
            
        Returns:
            Tuple of (value, description) for the selected option
        """
        question.display()
        
        valid_choices = list(question.options.keys())
        
        while True:
            choice = input(f"Your choice ({'-'.join(valid_choices)}): ").strip()
            
            if choice in question.options:
                value, description = question.options[choice]
                print(f"   ✓ Selected: {description.split(' - ')[0]}")
                return value, description
            
            print(retry_message)
    
    @staticmethod
    def get_demo_choice() -> Optional[DemoProfile]:
        """
        Get demo profile selection from user.
        
        Returns:
            Selected DemoProfile or None if invalid
        """
        print("\nChoose a demo profile:")
        for i, profile in enumerate(DemoProfiles.PROFILES, 1):
            print(f"  [{i}] {profile.name}")
            print(f"      {profile.description}")
        print()
        
        choice = input(f"Your choice (1-{len(DemoProfiles.PROFILES)}): ").strip()
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(DemoProfiles.PROFILES):
                return DemoProfiles.PROFILES[index]
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def get_mode_choice() -> str:
        """
        Get test mode selection from user.
        
        Returns:
            Mode choice as string ("1", "2", or "3")
        """
        print("Choose test mode:")
        print("  [1] Interactive Quiz (recommended)")
        print("  [2] Free-form Text Description")
        print("  [3] Quick Demo (predefined examples)")
        print()
        
        return input("Your choice (1-3): ").strip()
    
    @staticmethod
    def get_text_input(min_length: int = 10) -> str:
        """
        Get free-form text input from user.
        
        Args:
            min_length: Minimum required text length
            
        Returns:
            User's text input
        """
        print("\nYour description (minimum 10 characters):")
        return input("-> ").strip()


class QuizCollector:
    """Collects personality preferences through quiz interaction."""
    
    def __init__(self, input_handler: Optional[QuizInputHandler] = None):
        """
        Initialize quiz collector.
        
        Args:
            input_handler: Input handler (injectable for testing)
        """
        self.input_handler = input_handler or QuizInputHandler()
    
    def collect_preferences(self) -> PersonalityPreferences:
        """
        Collect personality preferences through interactive quiz.
        
        Returns:
            PersonalityPreferences from user input
        """
        print("\n" + "-"*70)
        print("INTERACTIVE PERSONALITY QUIZ")
        print("-"*70)
        print()
        
        # Question 1: Battle Style
        battle_style_value, _ = self.input_handler.get_choice(
            QuizQuestions.BATTLE_STYLE
        )
        
        print("\n" + "-"*70)
        
        # Question 2: Preferred Stat
        preferred_stat_value, _ = self.input_handler.get_choice(
            QuizQuestions.PREFERRED_STAT
        )
        
        print("\n" + "-"*70)
        
        # Question 3: Element Preference
        element_value, _ = self.input_handler.get_choice(
            QuizQuestions.ELEMENT_PREFERENCE
        )
        
        # Build preferences object
        return PersonalityPreferences(
            battle_style=BattleStyle(battle_style_value),
            preferred_stat=PreferredStat(preferred_stat_value),
            element_preference=ElementPreference(element_value)
        )
