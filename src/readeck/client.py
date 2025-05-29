"""Readeck API client implementation."""

from typing import Any, Dict, List, Optional, Union
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
from .models import (
    Bookmark,
    BookmarkCreateRequest,
    BookmarkCreateResponse,
    BookmarkCreateResult,
    BookmarkListParams,
    UserProfile,
)


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
    ) -> Union[Dict[str, Any], List[Any]]:
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
                json_response: Union[Dict[str, Any], List[Any]] = response.json()
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

    async def get_bookmarks(
        self, params: Optional[BookmarkListParams] = None
    ) -> List[Bookmark]:
        """Get a list of bookmarks.

        Args:
            params: Optional parameters for filtering and pagination

        Returns:
            List[Bookmark]: List of bookmark objects

        Raises:
            ReadeckAuthError: If authentication fails
            ReadeckError: For other API errors
        """
        try:
            query_params = params.to_query_params() if params else {}
            data = await self._make_request("GET", "bookmarks", params=query_params)

            # The API returns a list of bookmark objects directly
            if isinstance(data, list):
                return [Bookmark.model_validate(bookmark) for bookmark in data]
            else:
                raise ReadeckError(
                    f"Unexpected response format: expected list, got {type(data)}"
                )
        except ValidationError as e:
            raise ReadeckError(f"Failed to parse bookmarks response: {e}")

    async def create_bookmark(
        self, url: str, title: Optional[str] = None, labels: Optional[List[str]] = None
    ) -> BookmarkCreateResult:
        """Create a new bookmark.

        Args:
            url: The URL to bookmark
            title: Optional title for the bookmark
            labels: Optional list of labels for the bookmark

        Returns:
            BookmarkCreateResult: Result containing response data and headers

        Raises:
            ReadeckAuthError: If authentication fails
            ReadeckValidationError: If request validation fails
            ReadeckError: For other API errors
        """
        try:
            # Prepare request payload
            request_data = BookmarkCreateRequest(
                url=url, title=title, labels=labels or []
            )

            # Make the request
            url_endpoint = self._build_url("bookmarks")
            response = await self._client.post(
                url_endpoint,
                json=request_data.model_dump(exclude_none=True),
                headers={"Content-Type": "application/json"},
            )

            # Handle different status codes
            if response.status_code == 401:
                raise ReadeckAuthError(
                    "Authentication failed. Please check your token.",
                    status_code=response.status_code,
                )
            elif response.status_code == 403:
                raise ReadeckAuthError(
                    "Access forbidden. Insufficient permissions.",
                    status_code=response.status_code,
                )
            elif response.status_code == 422:
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
            elif response.status_code == 202:
                # 202 Accepted - bookmark creation accepted
                pass
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
                json_response = response.json()
            except Exception as e:
                raise ReadeckError(f"Failed to parse JSON response: {e}")

            try:
                bookmark_response = BookmarkCreateResponse.model_validate(json_response)

                # Extract headers
                bookmark_id = response.headers.get("Bookmark-Id")
                location = response.headers.get("Location")

                return BookmarkCreateResult(
                    response=bookmark_response,
                    bookmark_id=bookmark_id,
                    location=location,
                )
            except ValidationError as e:
                raise ReadeckError(f"Failed to parse bookmark creation response: {e}")

        except httpx.TimeoutException as e:
            raise ReadeckError(f"Request timeout: {e}")
        except httpx.RequestError as e:
            raise ReadeckError(f"Request error: {e}")

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
