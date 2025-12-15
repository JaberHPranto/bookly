from typing import Callable, Any, Coroutine
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class BooklyException(Exception):
    """Base exception for Bookly application errors."""
    pass

class InvalidTokenException(BooklyException):
    """Exception raised for invalid authentication tokens."""
    pass

class AccessTokenRequiredException(BooklyException):
    """Exception raised when an access token is required but not provided."""
    pass

class RefreshTokenRequiredException(BooklyException):
    """Exception raised when a refresh token is required but not provided."""
    pass

class UserNotFoundException(BooklyException):
    """Exception raised when a user is not found."""
    pass

class BookNotFoundException(BooklyException):
    """Exception raised when a book is not found."""
    pass

class InsufficientPermissionsException(BooklyException):
    """Exception raised when a user does not have sufficient permissions."""
    pass

class InvalidCredentialsException(BooklyException):
    """Exception raised for invalid user credentials."""
    pass


def create_exception_handler(status_code: int,initial_details:Any) -> Callable[[Request, Exception], Coroutine[Any, Any, JSONResponse]]:
    """Factory function to create exception handlers for Bookly exceptions."""

    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            content=initial_details,
            status_code=status_code,
        )
        
    return exception_handler