"""
Personality Test Facade

Orchestrates personality test operations using Facade pattern.
Coordinates between UI, service, and presentation layers.
"""

from typing import Optional
from core.personality_models import PersonalityPreferences
from core.exceptions import ValidationError, ExternalAPIError
from services.personality_test_service import (
    PersonalityTestService,
    get_personality_test_service
)
from services.personality_quiz_ui import (
    QuizCollector,
    QuizInputHandler,
    DemoProfiles
)
from services.personality_presenter import ResultPresenter


class PersonalityTestFacade:
    """
    Facade for personality test operations.
    
    Simplifies complex interactions between multiple subsystems.
    Follows Facade pattern to provide unified interface.
    """
    
    def __init__(
        self,
        service: Optional[PersonalityTestService] = None,
        quiz_collector: Optional[QuizCollector] = None,
        presenter: Optional[ResultPresenter] = None,
        input_handler: Optional[QuizInputHandler] = None
    ):
        """
        Initialize personality test facade.
        
        Args:
            service: Personality test service (injectable for testing)
            quiz_collector: Quiz collector (injectable for testing)
            presenter: Result presenter (injectable for testing)
            input_handler: Input handler (injectable for testing)
        """
        self.service = service or get_personality_test_service()
        self.quiz_collector = quiz_collector or QuizCollector()
        self.presenter = presenter or ResultPresenter()
        self.input_handler = input_handler or QuizInputHandler()
    
    async def run_interactive_quiz(self) -> None:
        """
        Run interactive personality quiz mode.
        
        Orchestrates: input collection -> API call -> result presentation
        """
        try:
            # Collect preferences through quiz
            preferences = self.quiz_collector.collect_preferences()
            
            # Show analysis start
            self.presenter.present_analysis_start(preferences)
            
            # Analyze personality using service
            async with self.service as svc:
                result = await svc.analyze_personality(preferences)
            
            # Present results
            self.presenter.present_result(result)
            
        except ValidationError as e:
            self.presenter.present_error(
                e.message,
                f"Field: {e.field}"
            )
        except ExternalAPIError as e:
            self.presenter.present_error(
                e.message,
                "Make sure the API server is running: uvicorn main:app --reload"
            )
        except Exception as e:
            self.presenter.present_error(
                f"Unexpected error: {str(e)}"
            )
    
    async def run_text_analysis(self) -> None:
        """
        Run free-form text analysis mode.
        
        Orchestrates: text input -> AI interpretation -> API call -> result presentation
        """
        print("\n" + "-"*70)
        print("FREE-FORM PERSONALITY ANALYSIS")
        print("-"*70)
        print()
        print("Describe yourself in your own words!")
        print()
        print("Examples:")
        print("• 'I'm very competitive and always rush into challenges.'")
        print("• 'I prefer to think things through and protect what matters.'")
        print("• 'I value creativity and finding unique solutions.'")
        print("• 'I'm adaptable and balanced, handling any situation.'")
        print()
        
        try:
            # Get text input
            user_text = self.input_handler.get_text_input()
            
            if not user_text:
                self.presenter.present_error("Empty description")
                return
            
            if len(user_text) < 10:
                self.presenter.present_error(
                    "Description too short",
                    "Please provide more detail (at least 10 characters)."
                )
                return
            
            print("\n[INFO] Analyzing your personality with AI...")
            print()
            
            # Analyze with AI using service
            async with self.service as svc:
                result = await svc.analyze_from_text(user_text)
            
            # Present results with interpretation
            self.presenter.present_text_result(result)
            
        except ValidationError as e:
            self.presenter.present_error(
                e.message,
                f"Field: {e.field}"
            )
        except ExternalAPIError as e:
            self.presenter.present_error(
                e.message,
                "Make sure the API server is running: uvicorn main:app --reload"
            )
        except Exception as e:
            self.presenter.present_error(
                f"Unexpected error: {str(e)}"
            )
    
    async def run_quick_demo(self) -> None:
        """
        Run quick demo mode with predefined profiles.
        
        Orchestrates: profile selection -> API call -> result presentation
        """
        print("\n" + "-"*70)
        print("QUICK DEMO - PERSONALITY PROFILES")
        print("-"*70)
        print()
        
        # Get profile selection
        profile = self.input_handler.get_demo_choice()
        
        if profile is None:
            self.presenter.present_error("Invalid choice")
            return
        
        try:
            # Show selected profile
            self.presenter.present_demo_profile(profile.name, profile.description)
            
            # Show analysis start
            self.presenter.present_analysis_start(profile.preferences)
            
            # Analyze personality using service
            async with self.service as svc:
                result = await svc.analyze_personality(profile.preferences)
            
            # Present results
            self.presenter.present_result(result)
            
        except ValidationError as e:
            self.presenter.present_error(
                e.message,
                f"Field: {e.field}"
            )
        except ExternalAPIError as e:
            self.presenter.present_error(
                e.message,
                "Make sure the API server is running: uvicorn main:app --reload"
            )
        except Exception as e:
            self.presenter.present_error(
                f"Unexpected error: {str(e)}"
            )
    
    async def check_server(self) -> bool:
        """
        Check if API server is available.
        
        Returns:
            True if server is healthy
        """
        async with self.service as svc:
            return await svc.check_server_health()


# Singleton instance
_facade_instance: Optional[PersonalityTestFacade] = None


def get_personality_test_facade() -> PersonalityTestFacade:
    """
    Get or create personality test facade singleton.
    
    Returns:
        PersonalityTestFacade instance
    """
    global _facade_instance
    if _facade_instance is None:
        _facade_instance = PersonalityTestFacade()
    return _facade_instance
