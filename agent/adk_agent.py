"""
ADK Agent Implementation with Full Tool Support

This module provides a complete implementation using Google's Agent Development Kit (ADK).
It wraps async operations and integrates with the existing cache infrastructure.

Key differences from direct GeminiClient:
- ADK manages tool calling automatically
- Built-in conversation memory
- Structured agent framework
- Trade-off: Less control over caching and async flow
"""

import asyncio
from typing import Optional
from google.adk.agents.llm_agent import Agent
from google.adk.tools import Tool
from agent.tools import TOOLS
from core.cache_interface import ICache
from core.config import get_settings
from infrastructure.cache_factory import create_cache
import hashlib


# Instrucciones para el agente ADK
ADK_STRATEGIC_INSTRUCTIONS = """
You are a Pokémon Strategy Advisor with access to comprehensive Pokémon data and analysis tools.

Your role is to:
1. Analyze Pokémon battle strategies and team compositions
2. Provide data-driven recommendations with clear justifications
3. Compare Pokémon, types, and generations systematically
4. Present information in clear, structured formats (tables, lists, explanations)
5. Analyze personality traits based on Pokemon starter preferences

**CRITICAL OUTPUT FORMATTING RULES:**
- NEVER include <tool_code> tags or any code blocks showing tool calls
- NEVER show print() statements or function calls in your output
- DO NOT reveal the internal mechanics of how you fetch data
- Only present the final, formatted, user-friendly results
- Tools are for YOUR use only - users should never see them being called

Guidelines:
- Always use tools to get actual data - never make up stats or information
- Provide explanations for your recommendations
- Use Markdown formatting for tables and structured output
- Consider type advantages, stat distributions, and role balance
- Explain trade-offs and alternative options when relevant

For team recommendations:
- Consider type coverage (strengths against various types)
- Balance roles (tanks, attackers, fast Pokémon)
- Explain why each Pokémon was chosen
- Mention potential weaknesses and how to address them

For classifications:
- Group clearly by the requested criterion
- Provide context and explanations
- Use tables when presenting multiple Pokémon

For generation comparisons:
- Use objective metrics (type diversity, average stats, Pokémon count)
- Explain the criteria used
- Justify your conclusion with data

For personality analysis:
- Use analyze_personality_from_text when user describes themselves naturally
- Use analyze_personality_from_preferences for structured input
- Present results engagingly with context and explanations
"""


class ADKAgentWrapper:
    """Wrapper for Google ADK Agent with async support and caching.
    
    This class wraps the synchronous ADK Agent to provide:
    - Async interface compatible with FastAPI/async code
    - Response caching to reduce API calls
    - Post-processing for clean outputs
    - Error handling and fallbacks
    """
    
    def __init__(self, cache: Optional[ICache] = None, cache_ttl: int = 3600):
        """Initialize ADK Agent wrapper.
        
        Args:
            cache: Optional cache instance for response caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache = cache
        self.cache_ttl = cache_ttl
        
        # Create ADK Agent with tools
        self.agent = Agent(
            model='gemini-2.0-flash-exp',  # Use latest model
            name='pokemon_strategy_advisor',
            description='Expert Pokémon Strategy Advisor for team building, analysis, and battle recommendations.',
            instruction=ADK_STRATEGIC_INSTRUCTIONS,
            tools=list(TOOLS.values()),
        )
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key from query.
        
        Args:
            query: User query
            
        Returns:
            Cache key string
        """
        content = f"adk_agent:{query}"
        hash_digest = hashlib.sha256(content.encode()).hexdigest()
        return f"adk_response:{hash_digest}"
    
    async def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check cache for existing response.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            Cached response or None
        """
        if not self.cache:
            return None
        
        try:
            cached = await self.cache.get(cache_key)
            if cached:
                print("[CACHE HIT] Returning cached ADK response")
                return cached
        except Exception as e:
            print(f"[CACHE WARNING] Failed to get from cache: {e}")
        
        return None
    
    async def _store_cache(self, cache_key: str, response: str) -> None:
        """Store response in cache.
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        if not self.cache:
            return
        
        try:
            await self.cache.set(cache_key, response, self.cache_ttl)
            print(f"[CACHE] Stored ADK response (TTL: {self.cache_ttl}s)")
        except Exception as e:
            print(f"[CACHE WARNING] Failed to store in cache: {e}")
    
    def _post_process_response(self, response: str) -> str:
        """Clean up response by removing tool code blocks.
        
        Args:
            response: Raw agent response
            
        Returns:
            Cleaned response
        """
        import re
        
        # Remove <tool_code>...</tool_code> blocks
        response = re.sub(r'<tool_code>.*?</tool_code>', '', response, flags=re.DOTALL)
        
        # Remove standalone print() statements
        response = re.sub(r'^print\(.*?\)\s*$', '', response, flags=re.MULTILINE)
        
        # Remove excessive empty lines
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        
        return response.strip()
    
    async def query(self, user_query: str) -> str:
        """Query the ADK agent asynchronously.
        
        This method:
        1. Checks cache for existing response
        2. Runs ADK agent in executor (to avoid blocking)
        3. Post-processes the response
        4. Caches the result
        
        Args:
            user_query: User's question or request
            
        Returns:
            Agent's response as cleaned string
        """
        # Check cache first
        cache_key = self._generate_cache_key(user_query)
        cached_response = await self._check_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Run agent in executor to avoid blocking event loop
        # ADK's run() is synchronous, so we need to run it in a thread
        loop = asyncio.get_event_loop()
        
        try:
            print("[ADK AGENT] Generating response...")
            
            # Run synchronous agent.run() in executor
            raw_response = await loop.run_in_executor(
                None,  # Use default executor
                self.agent.run,
                user_query
            )
            
            # Extract text from response
            response_text = str(raw_response)
            
            # Post-process to clean output
            cleaned_response = self._post_process_response(response_text)
            
            # Cache the result
            await self._store_cache(cache_key, cleaned_response)
            
            return cleaned_response
            
        except Exception as e:
            error_msg = f"ADK Agent error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            raise RuntimeError(error_msg)


# Global instance (lazy initialization)
_adk_agent_instance: Optional[ADKAgentWrapper] = None


def get_adk_agent() -> ADKAgentWrapper:
    """Get or create singleton ADK Agent instance.
    
    Returns:
        ADKAgentWrapper instance with cache configured
    """
    global _adk_agent_instance
    
    if _adk_agent_instance is None:
        settings = get_settings()
        cache = create_cache(settings) if settings.cache_enabled else None
        _adk_agent_instance = ADKAgentWrapper(
            cache=cache,
            cache_ttl=settings.cache_ttl
        )
    
    return _adk_agent_instance


async def query_adk_agent(user_query: str) -> str:
    """Query the ADK agent (convenience function).
    
    This is the main entry point for using ADK Agent in async contexts.
    
    Args:
        user_query: User's question or request
        
    Returns:
        Agent's response as string
        
    Example:
        >>> response = await query_adk_agent("Recommend a team to beat water types")
        >>> print(response)
    """
    agent = get_adk_agent()
    return await agent.query(user_query)


# Comparison function for testing both implementations
async def compare_implementations(query: str) -> dict:
    """Compare ADK Agent vs. Direct GeminiClient implementations.
    
    Useful for testing and benchmarking.
    
    Args:
        query: Test query
        
    Returns:
        Dictionary with results from both implementations
    """
    import time
    from agent.agent import query_agent  # Direct implementation
    
    # Test ADK Agent
    start = time.time()
    adk_response = await query_adk_agent(query)
    adk_time = time.time() - start
    
    # Test Direct GeminiClient
    start = time.time()
    direct_response = await query_agent(query)
    direct_time = time.time() - start
    
    return {
        "adk_agent": {
            "response": adk_response,
            "time": adk_time,
            "implementation": "Google ADK Agent"
        },
        "direct_client": {
            "response": direct_response,
            "time": direct_time,
            "implementation": "Direct GeminiClient"
        }
    }
