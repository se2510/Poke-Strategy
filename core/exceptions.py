"""Custom exception hierarchy for the application.

Provides consistent error handling across all modules with specific
exception types for different error scenarios.
"""

from typing import Optional, Dict, Any


class PokemonAPIException(Exception):
    """Base exception for all Pokemon API related errors.
    
    All custom exceptions inherit from this base class to enable
    consistent error handling and logging.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize exception with message and optional metadata.
        
        Args:
            message: Human-readable error description
            status_code: HTTP status code if applicable
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses.
        
        Returns:
            Dictionary containing error information
        """
        error_dict = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.status_code:
            error_dict["status_code"] = self.status_code
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class ExternalAPIError(PokemonAPIException):
    """Raised when external API (PokeAPI) encounters an error.
    
    Examples:
        - Network connectivity issues
        - API rate limiting (429)
        - Server errors (5xx)
        - Invalid API responses
    """
    
    def __init__(
        self, 
        message: str, 
        api_name: str = "PokeAPI",
        status_code: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize external API error.
        
        Args:
            message: Error description
            api_name: Name of the external API
            status_code: HTTP status code from API
            original_error: Original exception that caused this error
        """
        details = {"api": api_name}
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(message, status_code, details)
        self.api_name = api_name
        self.original_error = original_error


class ValidationError(PokemonAPIException):
    """Raised when input validation fails.
    
    Examples:
        - Empty Pokemon name
        - Invalid limit/offset values
        - Team size exceeds maximum
        - Invalid generation IDs
    """
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        """Initialize validation error.
        
        Args:
            message: Error description
            field: Name of the invalid field
            value: The invalid value provided
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(message, status_code=400, details=details)
        self.field = field
        self.value = value


class ResourceNotFoundError(PokemonAPIException):
    """Raised when a requested resource is not found.
    
    Examples:
        - Pokemon name doesn't exist
        - Invalid type name
        - Generation not found
    """
    
    def __init__(
        self, 
        resource_type: str, 
        resource_id: str
    ):
        """Initialize not found error.
        
        Args:
            resource_type: Type of resource (e.g., "Pokemon", "Type")
            resource_id: Identifier that wasn't found
        """
        message = f"{resource_type} '{resource_id}' not found"
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message, status_code=404, details=details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class CacheError(PokemonAPIException):
    """Raised when cache operations fail.
    
    Examples:
        - Redis connection failed
        - Cache serialization error
        - Cache key format error
    """
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize cache error.
        
        Args:
            message: Error description
            operation: Cache operation that failed (get/set/delete)
            original_error: Original exception
        """
        details = {}
        if operation:
            details["operation"] = operation
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(message, details=details)
        self.operation = operation
        self.original_error = original_error


class ConfigurationError(PokemonAPIException):
    """Raised when application configuration is invalid.
    
    Examples:
        - Missing required environment variables
        - Invalid cache type specified
        - Invalid timeout values
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None
    ):
        """Initialize configuration error.
        
        Args:
            message: Error description
            config_key: Configuration key that is invalid
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(message, details=details)
        self.config_key = config_key


class RateLimitError(PokemonAPIException):
    """Raised when rate limits are exceeded.
    
    Examples:
        - Too many requests in time window
        - API quota exceeded
    """
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit: Optional[int] = None
    ):
        """Initialize rate limit error.
        
        Args:
            message: Error description
            retry_after: Seconds to wait before retrying
            limit: Request limit per time window
        """
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        if limit:
            details["limit"] = limit
        
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after
        self.limit = limit
