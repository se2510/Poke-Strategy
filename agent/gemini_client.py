"""
Gemini API client module.

Provides a robust interface to interact with Google's Gemini models,
handling API versioning and model availability issues.
Includes response caching to reduce API calls and quota usage.
"""

from typing import Optional
import os
import hashlib
from dotenv import load_dotenv


class GeminiClient:
    """Client for interacting with Gemini API."""
    
    # Try models in order of preference (based on actual available models)
    MODELS_TO_TRY = [
        "gemini-2.5-flash",
        "gemini-2.5-pro-preview-06-05",
        "gemini-2.5-pro-preview-05-06",
        "gemini-2.5-pro-preview-03-25",
        "gemini-2.0-flash-exp",
    ]
    
    def __init__(self, api_key: Optional[str] = None, cache=None, cache_ttl: int = 3600):
        """Initialize Gemini client.
        
        Args:
            api_key: Google AI API key. If None, loads from environment.
            cache: ICache instance for response caching. If None, no caching.
            cache_ttl: Time-to-live for cached responses in seconds (default: 1 hour).
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self._working_model = None
        self._client = None
        self._cache = cache
        self._cache_ttl = cache_ttl
    
    def _get_client(self):
        """Get or create Gemini client."""
        if self._client is None:
            import google.genai as genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    def _list_available_models(self) -> list[str]:
        """List available models from the API.
        
        Returns:
            List of available model names
        """
        try:
            client = self._get_client()
            models = client.models.list()
            # Extract model names
            available = []
            for model in models:
                if hasattr(model, 'name'):
                    # Remove 'models/' prefix if present
                    name = model.name.replace('models/', '')
                    available.append(name)
            return available
        except Exception:
            # If listing fails, return empty list
            return []
    
    def _generate_cache_key(self, prompt: str, system_instruction: str) -> str:
        """Generate cache key from prompt and system instruction.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction
            
        Returns:
            Cache key string
        """
        # Create deterministic key from prompt + system_instruction
        content = f"{system_instruction}||{prompt}"
        hash_digest = hashlib.sha256(content.encode()).hexdigest()
        return f"agent_response:{hash_digest}"
    
    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        """Generate text using Gemini API with response caching.
        
        Args:
            prompt: The user's prompt
            system_instruction: System instructions for the model
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If no working model is found
        """
        import google.genai as genai
        from google.genai.types import GenerateContentConfig, Content, Part
        
        # Check cache first (sync wrapper for async cache)
        if self._cache:
            import asyncio
            cache_key = self._generate_cache_key(prompt, system_instruction)
            
            # Try to get from cache
            try:
                loop = asyncio.get_event_loop()
                cached_response = loop.run_until_complete(self._cache.get(cache_key))
                if cached_response:
                    print(f"[CACHE HIT] Returning cached response")
                    return cached_response
            except Exception as e:
                print(f"[CACHE WARNING] Failed to get from cache: {e}")
        
        # Get client
        client = self._get_client()
        
        # If we have a working model, try it first
        models_to_try = ([self._working_model] + self.MODELS_TO_TRY) if self._working_model else self.MODELS_TO_TRY
        
        # Try each model until one works
        last_error = None
        for model_name in models_to_try:
            try:
                # Prepare content
                full_prompt = f"{system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
                content = Content(
                    role="user",
                    parts=[Part(text=full_prompt)]
                )
                
                # Generate response
                response = client.models.generate_content(
                    model=model_name,
                    contents=[content],
                    config=GenerateContentConfig(temperature=0.7)
                )
                
                # If successful, cache this model and return
                if model_name != self._working_model:
                    self._working_model = model_name
                    print(f"[INFO] Using Gemini model: {model_name}")
                
                # Cache the response
                if self._cache:
                    try:
                        import asyncio
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(
                            self._cache.set(cache_key, response.text, self._cache_ttl)
                        )
                        print(f"[CACHE] Stored response (TTL: {self._cache_ttl}s)")
                    except Exception as e:
                        print(f"[CACHE WARNING] Failed to store in cache: {e}")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                # If quota exhausted, try next model instead of failing immediately
                if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                    last_error = e
                    print(f"[WARNING] Model {model_name} quota exhausted, trying next model...")
                    continue
                
                # For other errors, also try next model
                last_error = e
                continue
        
        # No model worked - provide helpful error message
        available = self._list_available_models()
        error_details = f"Last error: {last_error}"
        if available:
            error_details += f"\n\nAvailable models: {', '.join(available[:5])}"
        
        raise RuntimeError(
            f"Failed to connect to any Gemini model.\n{error_details}"
        )
    
    async def generate_text_async(self, prompt: str, system_instruction: str = "") -> str:
        """Async version of generate_text with proper async cache support.
        
        Args:
            prompt: The user's prompt
            system_instruction: System instructions for the model
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If no working model is found
        """
        import google.genai as genai
        from google.genai.types import GenerateContentConfig, Content, Part
        
        # Check cache first (async)
        if self._cache:
            cache_key = self._generate_cache_key(prompt, system_instruction)
            
            try:
                cached_response = await self._cache.get(cache_key)
                if cached_response:
                    print(f"[CACHE HIT] Returning cached response")
                    return cached_response
            except Exception as e:
                print(f"[CACHE WARNING] Failed to get from cache: {e}")
        
        # Get client
        client = self._get_client()
        
        # If we have a working model, try it first
        models_to_try = ([self._working_model] + self.MODELS_TO_TRY) if self._working_model else self.MODELS_TO_TRY
        
        # Try each model until one works
        last_error = None
        for model_name in models_to_try:
            try:
                # Prepare content
                full_prompt = f"{system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
                content = Content(
                    role="user",
                    parts=[Part(text=full_prompt)]
                )
                
                # Generate response
                response = client.models.generate_content(
                    model=model_name,
                    contents=[content],
                    config=GenerateContentConfig(temperature=0.7)
                )
                
                # If successful, cache this model and return
                if model_name != self._working_model:
                    self._working_model = model_name
                    print(f"[INFO] Using Gemini model: {model_name}")
                
                # Cache the response (async)
                if self._cache:
                    try:
                        await self._cache.set(cache_key, response.text, self._cache_ttl)
                        print(f"[CACHE] Stored response (TTL: {self._cache_ttl}s)")
                    except Exception as e:
                        print(f"[CACHE WARNING] Failed to store in cache: {e}")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                # If quota exhausted, try next model instead of failing immediately
                if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                    last_error = e
                    print(f"[WARNING] Model {model_name} quota exhausted, trying next model...")
                    continue
                
                # For other errors, also try next model
                last_error = e
                continue
        
        # No model worked - provide helpful error message
        available = self._list_available_models()
        error_details = f"Last error: {last_error}"
        if available:
            error_details += f"\n\nAvailable models: {', '.join(available[:5])}"
        
        raise RuntimeError(
            f"Failed to connect to any Gemini model.\n{error_details}"
        )
