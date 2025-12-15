import logging
from typing import Callable, Any, Coroutine
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


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


def create_exception_handler(
    status_code: int, initial_details: Any
) -> Callable[[Request, Exception], Coroutine[Any, Any, JSONResponse]]:
    """Factory function to create exception handlers for Bookly exceptions."""

    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            content=initial_details,
            status_code=status_code,
        )

    return exception_handler


def register_all_error_handlers(app: FastAPI) -> None:
    """
    Register all custom error handlers for the Bookly application.
    
    This function centralizes all exception handler registrations to improve
    maintainability and reduce code duplication in the main application file.
    
    Args:
        app: FastAPI application instance
    """
    
    # Define error handler configurations
    error_handlers_config = [
        {
            "exception": InvalidCredentialsException,
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "details": {
                "message": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS",
            },
        },
        {
            "exception": InvalidTokenException,
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "details": {
                "message": "Token is invalid or expired.",
                "error_code": "INVALID_TOKEN",
            },
        },
        {
            "exception": UserNotFoundException,
            "status_code": status.HTTP_404_NOT_FOUND,
            "details": {
                "message": "User not found",
                "error_code": "USER_NOT_FOUND",
            },
        },
        {
            "exception": BookNotFoundException,
            "status_code": status.HTTP_404_NOT_FOUND,
            "details": {
                "message": "Book not found",
                "error_code": "BOOK_NOT_FOUND",
            },
        },
        {
            "exception": InsufficientPermissionsException,
            "status_code": status.HTTP_403_FORBIDDEN,
            "details": {
                "message": "You do not have permission to perform this action",
                "error_code": "INSUFFICIENT_PERMISSIONS",
            },
        },
    ]
    
    # Register all exception handlers
    for config in error_handlers_config:
        app.add_exception_handler(
            config["exception"],
            create_exception_handler(
                status_code=config["status_code"],
                initial_details=config["details"],
            ),
        )
    
    # Register internal server error handler
    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"🚨 Internal server error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An internal server error occurred.",
                "error_code": "INTERNAL_SERVER_ERROR",
            },
        )