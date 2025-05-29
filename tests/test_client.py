"""Tests for the Readeck API client."""

import pytest
from pytest_httpx import HTTPXMock

from readeck import ReadeckClient
from readeck.exceptions import (
    ReadeckAuthError,
    ReadeckError,
    ReadeckNotFoundError,
    ReadeckServerError,
    ReadeckValidationError,
)
from readeck.models import UserProfile


class TestReadeckClientInit:
    """Test ReadeckClient initialization."""

    def test_client_initialization(self):
        """Test basic client initialization."""
        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        assert client.base_url == "https://test.readeck.com"
        assert client.token == "test_token"
        assert "Bearer test_token" in client._client.headers["Authorization"]

    def test_client_initialization_with_trailing_slash(self):
        """Test client initialization with trailing slash in base_url."""
        client = ReadeckClient(base_url="https://test.readeck.com/", token="test_token")

        # Should strip trailing slash
        assert client.base_url == "https://test.readeck.com"

    def test_client_custom_headers(self):
        """Test client initialization with custom headers."""
        custom_headers = {"Custom-Header": "custom-value"}
        client = ReadeckClient(
            base_url="https://test.readeck.com",
            token="test_token",
            headers=custom_headers,
        )

        assert client._client.headers["Custom-Header"] == "custom-value"
        assert "Bearer test_token" in client._client.headers["Authorization"]

    def test_build_url(self):
        """Test URL building."""
        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        url = client._build_url("profile")
        assert url == "https://test.readeck.com/api/profile"

        url = client._build_url("/profile")
        assert url == "https://test.readeck.com/api/profile"


class TestReadeckClientRequests:
    """Test ReadeckClient HTTP requests."""

    @pytest.mark.asyncio
    async def test_successful_request(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test successful HTTP request."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/test",
            json={"success": True},
        )

        result = await async_readeck_client._make_request("GET", "test")
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_auth_error_401(self, async_readeck_client, httpx_mock: HTTPXMock):
        """Test authentication error (401)."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            status_code=401,
            text="Unauthorized",
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await async_readeck_client._make_request("GET", "profile")

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_not_found_error_404(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test not found error (404)."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/nonexistent",
            status_code=404,
            text="Not Found",
        )

        with pytest.raises(ReadeckNotFoundError) as exc_info:
            await async_readeck_client._make_request("GET", "nonexistent")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_validation_error_400(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test validation error (400)."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/test",
            status_code=400,
            json={"detail": "Invalid request"},
        )

        with pytest.raises(ReadeckValidationError) as exc_info:
            await async_readeck_client._make_request("POST", "test")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_validation_error_422(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test validation error (422)."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/test",
            status_code=422,
            json={"detail": "Validation failed"},
        )

        with pytest.raises(ReadeckValidationError) as exc_info:
            await async_readeck_client._make_request("POST", "test")

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_server_error_500(self, async_readeck_client, httpx_mock: HTTPXMock):
        """Test server error (500)."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/test",
            status_code=500,
            text="Internal Server Error",
        )

        with pytest.raises(ReadeckServerError) as exc_info:
            await async_readeck_client._make_request("GET", "test")

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_generic_http_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test generic HTTP error."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/test",
            status_code=418,  # I'm a teapot
            text="I'm a teapot",
        )

        with pytest.raises(ReadeckError) as exc_info:
            await async_readeck_client._make_request("GET", "test")

        assert exc_info.value.status_code == 418
        assert "418" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_json_response(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test invalid JSON response."""
        httpx_mock.add_response(
            method="GET", url="https://test.readeck.com/api/test", text="Invalid JSON{"
        )

        with pytest.raises(ReadeckError) as exc_info:
            await async_readeck_client._make_request("GET", "test")

        assert "Failed to parse JSON response" in str(exc_info.value)


class TestGetUserProfile:
    """Test get_user_profile method."""

    @pytest.mark.asyncio
    async def test_get_user_profile_success(
        self, async_readeck_client, httpx_mock: HTTPXMock, mock_user_profile_data
    ):
        """Test successful user profile retrieval."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            json=mock_user_profile_data,
        )

        profile = await async_readeck_client.get_user_profile()

        assert isinstance(profile, UserProfile)
        assert profile.user.username == "testuser"
        assert profile.user.email == "test@example.com"
        assert profile.provider.application == ""
        assert profile.user.settings.reader_settings.font == "lora"

    @pytest.mark.asyncio
    async def test_get_user_profile_auth_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test user profile retrieval with auth error."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            status_code=401,
            text="Unauthorized",
        )

        with pytest.raises(ReadeckAuthError):
            await async_readeck_client.get_user_profile()

    @pytest.mark.asyncio
    async def test_get_user_profile_invalid_response(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test user profile retrieval with invalid response data."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            json={"invalid": "data"},
        )

        with pytest.raises(ReadeckError) as exc_info:
            await async_readeck_client.get_user_profile()

        assert "Failed to parse user profile response" in str(exc_info.value)


class TestHealthCheck:
    """Test health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(
        self, async_readeck_client, httpx_mock: HTTPXMock, mock_user_profile_data
    ):
        """Test successful health check."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            json=mock_user_profile_data,
        )

        is_healthy = await async_readeck_client.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_health_check_failure(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test failed health check."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            status_code=401,
            text="Unauthorized",
        )

        is_healthy = await async_readeck_client.health_check()
        assert is_healthy is False


class TestContextManager:
    """Test async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager(self, httpx_mock: HTTPXMock, mock_user_profile_data):
        """Test using client as async context manager."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/profile",
            json=mock_user_profile_data,
        )

        async with ReadeckClient(
            base_url="https://test.readeck.com", token="test_token"
        ) as client:
            profile = await client.get_user_profile()
            assert profile.user.username == "testuser"

        # Client should be closed after context manager exits
        assert client._client.is_closed


class TestReadeckClientBookmarks:
    """Test ReadeckClient bookmark operations."""

    @pytest.mark.asyncio
    async def test_get_bookmarks_empty_list(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test getting an empty list of bookmarks."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks",
            json=[],
        )

        bookmarks = await async_readeck_client.get_bookmarks()
        assert bookmarks == []

    @pytest.mark.asyncio
    async def test_get_bookmarks_with_data(
        self, async_readeck_client, httpx_mock: HTTPXMock, mock_bookmark_data
    ):
        """Test getting bookmarks with data."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks",
            json=[mock_bookmark_data],
        )

        bookmarks = await async_readeck_client.get_bookmarks()
        assert len(bookmarks) == 1

        bookmark = bookmarks[0]
        assert bookmark.id == "abc123"
        assert bookmark.title == "Example Article"
        assert bookmark.url == "https://example.com/article"
        assert bookmark.type == "article"
        assert bookmark.is_marked is False
        assert bookmark.is_archived is False
        assert len(bookmark.authors) == 1
        assert bookmark.authors[0] == "John Doe"

    @pytest.mark.asyncio
    async def test_get_bookmarks_with_params(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test getting bookmarks with filtering parameters."""
        import re

        from readeck.models import BookmarkListParams

        params = BookmarkListParams(
            limit=10,
            offset=20,
            search="python",
            is_marked=True,
            type=["article"],
            sort=["created", "-title"],
        )

        # Mock the request using regex to match URL with any query parameters
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"https://test\.readeck\.com/api/bookmarks.*"),
            json=[],
        )

        bookmarks = await async_readeck_client.get_bookmarks(params)
        assert bookmarks == []

    @pytest.mark.asyncio
    async def test_get_bookmarks_with_datetime_params(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test getting bookmarks with datetime parameters."""
        import re
        from datetime import datetime

        from readeck.models import BookmarkListParams

        updated_since = datetime(2024, 1, 1, 12, 0, 0)
        params = BookmarkListParams(updated_since=updated_since)

        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"https://test\.readeck\.com/api/bookmarks.*"),
            json=[],
        )

        bookmarks = await async_readeck_client.get_bookmarks(params)
        assert bookmarks == []

    @pytest.mark.asyncio
    async def test_get_bookmarks_invalid_response_format(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test handling of invalid response format."""
        # Return object instead of list
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks",
            json={"error": "not a list"},
        )

        with pytest.raises(ReadeckError) as exc_info:
            await async_readeck_client.get_bookmarks()

        assert "Unexpected response format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_bookmarks_validation_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test handling of invalid bookmark data."""
        # Return bookmark with missing required fields
        invalid_bookmark = {"id": "123"}  # Missing required fields

        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks",
            json=[invalid_bookmark],
        )

        with pytest.raises(ReadeckError) as exc_info:
            await async_readeck_client.get_bookmarks()

        assert "Failed to parse bookmarks response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_bookmarks_auth_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test authentication error when getting bookmarks."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks",
            status_code=401,
            text="Unauthorized",
        )

        with pytest.raises(ReadeckAuthError):
            await async_readeck_client.get_bookmarks()

    @pytest.mark.asyncio
    async def test_get_bookmarks_server_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test server error when getting bookmarks."""
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks",
            status_code=500,
            text="Internal Server Error",
        )

        with pytest.raises(ReadeckServerError):
            await async_readeck_client.get_bookmarks()
