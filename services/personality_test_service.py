"""
Personality Test Service Implementation

Implements the personality test business logic, communicating with API endpoints.
Follows Single Responsibility and Dependency Inversion principles.
"""

import httpx
from typing import Optional
from core.personality_interface import IPersonalityTestService
from core.personality_models import (
    PersonalityPreferences,
    PersonalityResult,
    TextAnalysisResult
)
from core.exceptions import ValidationError, ExternalAPIError
from core.config import get_settings


class PersonalityTestService(IPersonalityTestService):
    """
    Service for personality test operations.
    
    Handles communication with the Pokemon API for personality analysis.
    Separates business logic from presentation layer (CLI).
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize personality test service.
        
        Args:
            base_url: Base URL for API (defaults to config)
            timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.base_url = base_url or "http://localhost:8000"
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def analyze_personality(
        self,
        preferences: PersonalityPreferences
    ) -> PersonalityResult:
        """
        Analyze personality based on structured preferences.
        
        Args:
            preferences: User personality preferences
            
        Returns:
            PersonalityResult with matched Pokemon and traits
            
        Raises:
            ValidationError: If preferences are invalid
            ExternalAPIError: If API call fails
        """
        # Validate preferences
        self.validate_preferences(preferences)
        
        # Make API call
        try:
            if self._client is None:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/pokemon/personality/analyze",
                        json=preferences.to_dict()
                    )
            else:
                response = await self._client.post(
                    f"{self.base_url}/pokemon/personality/analyze",
                    json=preferences.to_dict()
                )
            
            if response.status_code == 200:
                data = response.json()
                return PersonalityResult.from_api_response(data)
            elif response.status_code == 400:
                error_data = response.json()
                raise ValidationError(
                    message=error_data.get("detail", {}).get("message", "Validation error"),
                    field=error_data.get("detail", {}).get("field", "unknown"),
                    value=error_data.get("detail", {}).get("value", "")
                )
            else:
                raise ExternalAPIError(
                    message=f"API returned status {response.status_code}",
                    status_code=response.status_code
                )
                
        except httpx.ConnectError as e:
            raise ExternalAPIError(
                message="Cannot connect to API server. Ensure it's running.",
                status_code=503
            ) from e
        except (ValidationError, ExternalAPIError):
            raise
        except Exception as e:
            raise ExternalAPIError(
                message=f"Unexpected error: {str(e)}",
                status_code=500
            ) from e
    
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
        # Validate text
        if not user_text or not user_text.strip():
            raise ValidationError(
                message="User text cannot be empty",
                field="user_text",
                value=user_text
            )
        
        if len(user_text.strip()) < 10:
            raise ValidationError(
                message="Text too short. Please provide at least 10 characters.",
                field="user_text",
                value=user_text
            )
        
        # Make API call
        try:
            if self._client is None:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/pokemon/personality/analyze-from-text",
                        json={"user_text": user_text}
                    )
            else:
                response = await self._client.post(
                    f"{self.base_url}/pokemon/personality/analyze-from-text",
                    json={"user_text": user_text}
                )
            
            if response.status_code == 200:
                data = response.json()
                return TextAnalysisResult.from_api_response(data)
            elif response.status_code == 400:
                error_data = response.json()
                raise ValidationError(
                    message=error_data.get("detail", {}).get("message", "Validation error"),
                    field=error_data.get("detail", {}).get("field", "unknown"),
                    value=error_data.get("detail", {}).get("value", "")
                )
            else:
                raise ExternalAPIError(
                    message=f"API returned status {response.status_code}",
                    status_code=response.status_code
                )
                
        except httpx.ConnectError as e:
            raise ExternalAPIError(
                message="Cannot connect to API server. Ensure it's running.",
                status_code=503
            ) from e
        except (ValidationError, ExternalAPIError):
            raise
        except Exception as e:
            raise ExternalAPIError(
                message=f"Unexpected error: {str(e)}",
                status_code=500
            ) from e
    
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
        # Validation is already done by the Enum types
        # This is more of a semantic check
        if not isinstance(preferences, PersonalityPreferences):
            raise ValidationError(
                message="Invalid preferences object",
                field="preferences",
                value=str(preferences)
            )
        
        return True
    
    async def check_server_health(self) -> bool:
        """
        Check if API server is available.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            if self._client is None:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.base_url}/health")
            else:
                response = await self._client.get(f"{self.base_url}/health")
            
            return response.status_code == 200
        except:
            return False


# Singleton instance for dependency injection
_service_instance: Optional[PersonalityTestService] = None


def get_personality_test_service() -> PersonalityTestService:
    """
    Get or create personality test service singleton.
    
    Follows Dependency Injection pattern for testability.
    
    Returns:
        PersonalityTestService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = PersonalityTestService()
    return _service_instance
