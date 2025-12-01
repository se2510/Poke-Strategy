"""
Personality Result Presenter Module

Handles formatting and displaying personality test results.
Follows Single Responsibility Principle - only handles presentation.
"""

from typing import Optional
from core.personality_models import (
    PersonalityResult,
    TextAnalysisResult,
    PersonalityPreferences
)


class ResultFormatter:
    """Formats personality test results for display."""
    
    SEPARATOR_MAJOR = "=" * 70
    SEPARATOR_MINOR = "-" * 70
    
    @staticmethod
    def format_header(title: str) -> str:
        """Format a section header."""
        return f"\n{ResultFormatter.SEPARATOR_MAJOR}\n{title}\n{ResultFormatter.SEPARATOR_MAJOR}\n"
    
    @staticmethod
    def format_subheader(title: str) -> str:
        """Format a subsection header."""
        return f"\n{ResultFormatter.SEPARATOR_MINOR}\n{title}\n{ResultFormatter.SEPARATOR_MINOR}\n"
    
    @staticmethod
    def format_stat_bar(stat_name: str, value: int, max_value: int = 250) -> str:
        """
        Format a stat with visual bar.
        
        Args:
            stat_name: Name of the stat
            value: Stat value
            max_value: Maximum possible value for scaling
            
        Returns:
            Formatted stat bar string
        """
        bar_length = int((value / max_value) * 25)  # Scale to 25 chars max
        bar = "█" * bar_length + "░" * (25 - bar_length)
        formatted_name = stat_name.replace('-', ' ').title()
        return f"   {formatted_name:<20} [{bar}] {value}"
    
    @staticmethod
    def format_preferences(preferences: PersonalityPreferences) -> str:
        """Format user preferences for display."""
        lines = [
            "[INPUT] Your Preferences:",
            f"   Battle Style: {preferences.battle_style.value.capitalize()}",
            f"   Preferred Quality: {preferences.preferred_stat.value.replace('-', ' ').title()}",
            f"   Element: {preferences.element_preference.value.capitalize()}"
        ]
        return "\n".join(lines)


class ResultPresenter:
    """Presents personality test results to the user."""
    
    def __init__(self, formatter: Optional[ResultFormatter] = None):
        """
        Initialize result presenter.
        
        Args:
            formatter: Formatter instance (injectable for testing)
        """
        self.formatter = formatter or ResultFormatter()
    
    def present_analysis_start(self, preferences: PersonalityPreferences) -> None:
        """
        Display analysis start message.
        
        Args:
            preferences: User's personality preferences
        """
        print(self.formatter.format_header("ANALYZING YOUR PERSONALITY..."))
        print(self.formatter.format_preferences(preferences))
        print()
    
    def present_result(self, result: PersonalityResult) -> None:
        """
        Present personality analysis result.
        
        Args:
            result: PersonalityResult to display
        """
        print(self.formatter.format_header("YOUR POKEMON MATCH"))
        
        # Summary
        if result.summary:
            print(result.summary)
            print()
        
        # Main match
        print(self.formatter.format_subheader(
            f"✨ YOUR POKEMON: {result.matched_starter.upper()}"
        ))
        print(f"Match Score: {result.match_score}/100")
        print()
        
        # Personality traits
        print("[PERSONALITY TRAITS]")
        print("Your core characteristics based on Pokemon stats:")
        print()
        for i, trait in enumerate(result.personality_traits, 1):
            print(f"   {i}. {trait}")
        print()
        
        # Alternative matches
        if result.alternative_matches:
            print(self.formatter.format_subheader("[ALTERNATIVE MATCHES]"))
            print("Other Pokemon that also match your personality:")
            print()
            for match in result.alternative_matches:
                print(f"   • {match.name.title():<15} (Score: {match.score}/100)")
            print()
        
        # Stats breakdown
        if result.stats_mapping:
            print(self.formatter.format_subheader("[STATS BREAKDOWN]"))
            print()
            for stat, value in result.stats_mapping.items():
                print(self.formatter.format_stat_bar(stat, value))
            print()
        
        print(self.formatter.SEPARATOR_MAJOR)
    
    def present_text_result(self, result: TextAnalysisResult) -> None:
        """
        Present text analysis result with interpretation.
        
        Args:
            result: TextAnalysisResult to display
        """
        # Show interpretation
        print(self.formatter.format_subheader("[AI INTERPRETATION]"))
        print(f"Original Text: \"{result.interpretation.original_text}\"")
        print()
        print("[EXTRACTED] Your Personality Profile:")
        prefs = result.interpretation.extracted_preferences
        print(f"   Battle Style: {prefs.battle_style.value.capitalize()}")
        print(f"   Preferred Quality: {prefs.preferred_stat.value.replace('-', ' ').title()}")
        print(f"   Element: {prefs.element_preference.value.capitalize()}")
        print()
        print(f"Confidence: {result.interpretation.confidence.upper()}")
        if result.interpretation.reasoning:
            print(f"Reasoning: {result.interpretation.reasoning}")
        print()
        
        # Show regular results
        self.present_result(result)
    
    def present_error(self, error_message: str, suggestion: Optional[str] = None) -> None:
        """
        Present error message to user.
        
        Args:
            error_message: Error message to display
            suggestion: Optional suggestion for fixing the error
        """
        print(f"\n[ERROR] {error_message}")
        if suggestion:
            print(f"   {suggestion}")
        print()
    
    def present_demo_profile(self, profile_name: str, description: str) -> None:
        """
        Present selected demo profile.
        
        Args:
            profile_name: Name of the profile
            description: Profile description
        """
        print(f"\n[PROFILE] {profile_name}")
        print(f"   {description}")
