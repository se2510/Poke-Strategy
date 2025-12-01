"""
Personality Test Service Interface

Defines the contract for personality test services following SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from core.personality_models import (
    PersonalityPreferences,
    PersonalityResult,
    TextAnalysisResult
)


class IPersonalityTestService(ABC):
    """Interface for personality test service operations."""
    
    @abstractmethod
    async def analyze_personality(
        self,
        preferences: PersonalityPreferences
    ) -> PersonalityResult:
        """
        Analyze personality based on preferences.
        
        Args:
            preferences: User personality preferences
            
        Returns:
            PersonalityResult with matched Pokemon and traits
            
        Raises:
            ValidationError: If preferences are invalid
            ExternalAPIError: If API call fails
        """
        pass
    
    @abstractmethod
    async def analyze_from_text(
        self,
        user_text: str
    ) -> TextAnalysisResult:
        """
        Analyze personality from free-form text using AI.
        
        Args:
            user_text: Natural language description from user
            
        Returns:
            TextAnalysisResult with interpretation and match
            
        Raises:
            ValidationError: If text is invalid or too short
            ExternalAPIError: If API call fails
        """
        pass
    
    @abstractmethod
    def validate_preferences(
        self,
        preferences: PersonalityPreferences
    ) -> bool:
        """
        Validate personality preferences.
        
        Args:
            preferences: Preferences to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If preferences are invalid
        """
        pass
