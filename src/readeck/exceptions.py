"""Custom exceptions for the Readeck client."""

from typing import Any, Optional


class ReadeckError(Exception):
    """Base exception for all Readeck client errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
    ) -> None:
        """Initialize ReadeckError.

        Args:
            message: The error message.
            status_code: HTTP status code if applicable.
            response_data: Additional response data from the API.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class ReadeckAuthError(ReadeckError):
    """Raised when authentication fails."""

    pass


class ReadeckNotFoundError(ReadeckError):
    """Raised when a resource is not found."""

    pass


class ReadeckValidationError(ReadeckError):
    """Raised when request validation fails."""

    pass


class ReadeckServerError(ReadeckError):
    """Raised when the server returns a 5xx error."""

    pass
