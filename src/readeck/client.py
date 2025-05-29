"""Readeck API client implementation."""

from typing import Any, Dict
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError

from .exceptions import (
    ReadeckAuthError,
    ReadeckError,
    ReadeckNotFoundError,
    ReadeckServerError,
    ReadeckValidationError,
)
from .models import UserProfile


class ReadeckClient:
    """Async client for the Readeck API."""

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        **httpx_kwargs: Any,
    ) -> None:
        """Initialize the Readeck client.

        Args:
            base_url: The base URL of your Readeck instance (e.g., "https://readeck.example.com")
            token: Bearer token for authentication
            timeout: Request timeout in seconds
            **httpx_kwargs: Additional arguments passed to httpx.AsyncClient
        """
        self.base_url = base_url.rstrip("/")
        self.token = token

        # Default headers
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "readeck-python/0.1.0",
        }

        # Merge with any provided headers
        if "headers" in httpx_kwargs:
            headers.update(httpx_kwargs.pop("headers"))

        # Initialize the HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            **httpx_kwargs,
        )

    async def __aenter__(self) -> "ReadeckClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint."""
        return urljoin(f"{self.base_url}/", f"api/{endpoint.lstrip('/')}")

    async def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without /api/ prefix)
            **kwargs: Additional arguments for httpx request

        Returns:
            Parsed JSON response

        Raises:
            ReadeckAuthError: For authentication errors (401)
            ReadeckNotFoundError: For not found errors (404)
            ReadeckValidationError: For validation errors (400, 422)
            ReadeckServerError: For server errors (5xx)
            ReadeckError: For other HTTP errors
        """
        url = self._build_url(endpoint)

        try:
            response = await self._client.request(method, url, **kwargs)

            # Handle different status codes
            if response.status_code == 401:
                raise ReadeckAuthError(
                    "Authentication failed. Please check your token.",
                    status_code=response.status_code,
                )
            elif response.status_code == 404:
                raise ReadeckNotFoundError(
                    "Resource not found.",
                    status_code=response.status_code,
                )
            elif response.status_code in (400, 422):
                error_data = None
                try:
                    error_data = response.json()
                except Exception:
                    pass
                raise ReadeckValidationError(
                    f"Validation error: {response.text}",
                    status_code=response.status_code,
                    response_data=error_data,
                )
            elif 500 <= response.status_code < 600:
                raise ReadeckServerError(
                    f"Server error: {response.text}",
                    status_code=response.status_code,
                )
            elif not response.is_success:
                raise ReadeckError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )

            # Parse JSON response
            try:
                json_response: Dict[str, Any] = response.json()
                return json_response
            except Exception as e:
                raise ReadeckError(f"Failed to parse JSON response: {e}")

        except httpx.TimeoutException as e:
            raise ReadeckError(f"Request timeout: {e}")
        except httpx.RequestError as e:
            raise ReadeckError(f"Request error: {e}")

    async def get_user_profile(self) -> UserProfile:
        """Get the current user's profile.

        Returns:
            UserProfile: The user's profile information including settings

        Raises:
            ReadeckAuthError: If authentication fails
            ReadeckError: For other API errors
        """
        try:
            data = await self._make_request("GET", "profile")
            return UserProfile.model_validate(data)
        except ValidationError as e:
            raise ReadeckError(f"Failed to parse user profile response: {e}")

    # Health check method for testing connectivity
    async def health_check(self) -> bool:
        """Check if the Readeck instance is accessible.

        Returns:
            bool: True if the instance is accessible, False otherwise
        """
        try:
            await self.get_user_profile()
            return True
        except ReadeckError:
            return False
