"""Tests for personality interpreter service."""

import pytest
from services.personality_interpreter import PersonalityInterpreter, get_personality_interpreter
from core.exceptions import ValidationError


@pytest.fixture
def interpreter():
    """Create personality interpreter instance."""
    return PersonalityInterpreter()


class TestPersonalityInterpreter:
    """Test suite for PersonalityInterpreter."""
    
    @pytest.mark.asyncio
    async def test_interpret_aggressive_text(self, interpreter):
        """Test interpretation of aggressive personality text."""
        text = "I'm very competitive and love rushing into challenges with full force!"
        
        result = await interpreter.interpret_user_text(text)
        
        assert "battle_style" in result
        assert "preferred_stat" in result
        assert "element_preference" in result
        assert "confidence" in result
        assert "reasoning" in result
        
        # Should detect aggressive style
        assert result["battle_style"] in ["aggressive", "balanced", "tactical"]
        assert result["preferred_stat"] in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
        assert result["element_preference"] in ["fire", "water", "grass", "any"]
    
    @pytest.mark.asyncio
    async def test_interpret_defensive_text(self, interpreter):
        """Test interpretation of defensive personality text."""
        text = "I prefer to protect what's important and think carefully before acting."
        
        result = await interpreter.interpret_user_text(text)
        
        assert result["battle_style"] in ["defensive", "balanced", "tactical"]
        assert result["preferred_stat"] in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
    
    @pytest.mark.asyncio
    async def test_interpret_creative_text(self, interpreter):
        """Test interpretation of creative/tactical personality text."""
        text = "I love finding creative and innovative solutions to problems. Intelligence is key!"
        
        result = await interpreter.interpret_user_text(text)
        
        assert result["battle_style"] in ["tactical", "balanced"]
        assert result["preferred_stat"] in ["special-attack", "special-defense", "speed"]
    
    @pytest.mark.asyncio
    async def test_interpret_speed_focused_text(self, interpreter):
        """Test interpretation of speed-focused personality text."""
        text = "I'm all about being quick and adaptable. Speed and agility are my strengths!"
        
        result = await interpreter.interpret_user_text(text)
        
        # Should likely detect speed preference
        assert result["preferred_stat"] in ["speed", "attack", "special-attack"]
    
    @pytest.mark.asyncio
    async def test_interpret_with_element_mention(self, interpreter):
        """Test interpretation when element is mentioned."""
        text = "I'm passionate and fiery, always full of energy and heat!"
        
        result = await interpreter.interpret_user_text(text)
        
        # Should detect fire affinity
        assert result["element_preference"] in ["fire", "any"]
    
    @pytest.mark.asyncio
    async def test_empty_text_raises_error(self, interpreter):
        """Test that empty text raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            await interpreter.interpret_user_text("")
        
        assert "cannot be empty" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_too_short_text_raises_error(self, interpreter):
        """Test that too short text raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            await interpreter.interpret_user_text("short")
        
        assert "too short" in exc_info.value.message.lower()
    
    @pytest.mark.asyncio
    async def test_whitespace_only_raises_error(self, interpreter):
        """Test that whitespace-only text raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            await interpreter.interpret_user_text("   \n\t   ")
        
        assert "cannot be empty" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_result_has_all_required_fields(self, interpreter):
        """Test that result contains all required fields."""
        text = "I value balance and adaptability in everything I do."
        
        result = await interpreter.interpret_user_text(text)
        
        required_fields = ["battle_style", "preferred_stat", "element_preference", "confidence", "reasoning"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    @pytest.mark.asyncio
    async def test_confidence_is_valid(self, interpreter):
        """Test that confidence level is one of expected values."""
        text = "I'm decisive and direct in my approach to everything."
        
        result = await interpreter.interpret_user_text(text)
        
        assert result["confidence"] in ["high", "medium", "low"]
    
    @pytest.mark.asyncio
    async def test_reasoning_is_present(self, interpreter):
        """Test that reasoning explanation is provided."""
        text = "I'm methodical and protective of those I care about."
        
        result = await interpreter.interpret_user_text(text)
        
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0


class TestGetPersonalityInterpreter:
    """Test singleton pattern for interpreter."""
    
    def test_get_interpreter_returns_instance(self):
        """Test that get_personality_interpreter returns an instance."""
        interpreter = get_personality_interpreter()
        assert isinstance(interpreter, PersonalityInterpreter)
    
    def test_get_interpreter_returns_same_instance(self):
        """Test that get_personality_interpreter returns singleton."""
        interpreter1 = get_personality_interpreter()
        interpreter2 = get_personality_interpreter()
        assert interpreter1 is interpreter2
