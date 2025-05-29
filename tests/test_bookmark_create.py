"""Tests for bookmark creation functionality."""

import pytest
from pytest_httpx import HTTPXMock

from readeck import ReadeckClient
from readeck.exceptions import (
    ReadeckAuthError,
    ReadeckError,
    ReadeckServerError,
    ReadeckValidationError,
)
from readeck.models import (
    BookmarkCreateRequest,
    BookmarkCreateResponse,
    BookmarkCreateResult,
)


class TestBookmarkCreateModels:
    """Test bookmark creation models."""

    def test_bookmark_create_request_minimal(self):
        """Test creating a minimal bookmark request."""
        request = BookmarkCreateRequest(url="https://example.com")

        assert request.url == "https://example.com"
        assert request.title is None
        assert request.labels == []

    def test_bookmark_create_request_with_title(self):
        """Test creating a bookmark request with title."""
        request = BookmarkCreateRequest(
            url="https://example.com", title="Example Title"
        )

        assert request.url == "https://example.com"
        assert request.title == "Example Title"
        assert request.labels == []

    def test_bookmark_create_request_with_labels(self):
        """Test creating a bookmark request with labels."""
        request = BookmarkCreateRequest(
            url="https://example.com", labels=["tech", "python"]
        )

        assert request.url == "https://example.com"
        assert request.title is None
        assert request.labels == ["tech", "python"]

    def test_bookmark_create_request_complete(self):
        """Test creating a complete bookmark request."""
        request = BookmarkCreateRequest(
            url="https://example.com/article",
            title="Great Article",
            labels=["tech", "programming", "python"],
        )

        assert request.url == "https://example.com/article"
        assert request.title == "Great Article"
        assert request.labels == ["tech", "programming", "python"]

    def test_bookmark_create_request_model_dump(self):
        """Test model dump functionality."""
        request = BookmarkCreateRequest(
            url="https://example.com", title="Test Title", labels=["label1", "label2"]
        )

        data = request.model_dump(exclude_none=True)
        expected = {
            "url": "https://example.com",
            "title": "Test Title",
            "labels": ["label1", "label2"],
        }

        assert data == expected

    def test_bookmark_create_request_model_dump_minimal(self):
        """Test model dump with minimal data."""
        request = BookmarkCreateRequest(url="https://example.com")

        data = request.model_dump(exclude_none=True)
        expected = {"url": "https://example.com", "labels": []}

        assert data == expected

    def test_bookmark_create_response(self):
        """Test bookmark create response model."""
        response = BookmarkCreateResponse(
            message="Bookmark created successfully", status=0
        )

        assert response.message == "Bookmark created successfully"
        assert response.status == 0

    def test_bookmark_create_result(self):
        """Test bookmark create result model."""
        response = BookmarkCreateResponse(
            message="Bookmark created successfully", status=0
        )

        result = BookmarkCreateResult(
            response=response,
            bookmark_id="abc123",
            location="https://example.com/api/bookmarks/abc123",
        )

        assert result.response.message == "Bookmark created successfully"
        assert result.response.status == 0
        assert result.bookmark_id == "abc123"
        assert result.location == "https://example.com/api/bookmarks/abc123"

    def test_bookmark_create_result_without_headers(self):
        """Test bookmark create result without optional headers."""
        response = BookmarkCreateResponse(
            message="Bookmark created successfully", status=0
        )

        result = BookmarkCreateResult(response=response)

        assert result.response.message == "Bookmark created successfully"
        assert result.response.status == 0
        assert result.bookmark_id is None
        assert result.location is None


class TestBookmarkCreateClient:
    """Test bookmark creation in client."""

    @pytest.mark.asyncio
    async def test_create_bookmark_minimal(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test creating a bookmark with minimal data."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
            headers={
                "Bookmark-Id": "abc123",
                "Location": "https://test.readeck.com/api/bookmarks/abc123",
            },
        )

        result = await async_readeck_client.create_bookmark(url="https://example.com")

        assert isinstance(result, BookmarkCreateResult)
        assert result.response.message == "Bookmark created successfully"
        assert result.response.status == 0
        assert result.bookmark_id == "abc123"
        assert result.location == "https://test.readeck.com/api/bookmarks/abc123"

    @pytest.mark.asyncio
    async def test_create_bookmark_with_title(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test creating a bookmark with title."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
            headers={
                "Bookmark-Id": "def456",
                "Location": "https://test.readeck.com/api/bookmarks/def456",
            },
        )

        result = await async_readeck_client.create_bookmark(
            url="https://example.com/article", title="Great Article"
        )

        assert result.response.message == "Bookmark created successfully"
        assert result.bookmark_id == "def456"

    @pytest.mark.asyncio
    async def test_create_bookmark_with_labels(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test creating a bookmark with labels."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
            headers={
                "Bookmark-Id": "ghi789",
                "Location": "https://test.readeck.com/api/bookmarks/ghi789",
            },
        )

        result = await async_readeck_client.create_bookmark(
            url="https://example.com/tech-article", labels=["tech", "programming"]
        )

        assert result.response.message == "Bookmark created successfully"
        assert result.bookmark_id == "ghi789"

    @pytest.mark.asyncio
    async def test_create_bookmark_complete(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test creating a bookmark with all data."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
            headers={
                "Bookmark-Id": "complete123",
                "Location": "https://test.readeck.com/api/bookmarks/complete123",
            },
        )

        result = await async_readeck_client.create_bookmark(
            url="https://example.com/complete-article",
            title="Complete Article Title",
            labels=["tech", "programming", "python", "tutorial"],
        )

        assert result.response.message == "Bookmark created successfully"
        assert result.response.status == 0
        assert result.bookmark_id == "complete123"
        assert result.location == "https://test.readeck.com/api/bookmarks/complete123"

    @pytest.mark.asyncio
    async def test_create_bookmark_without_headers(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test creating a bookmark when server doesn't return optional headers."""
        # Mock the API response without optional headers
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
        )

        result = await async_readeck_client.create_bookmark(url="https://example.com")

        assert result.response.message == "Bookmark created successfully"
        assert result.response.status == 0
        assert result.bookmark_id is None
        assert result.location is None

    @pytest.mark.asyncio
    async def test_create_bookmark_auth_error(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test bookmark creation with authentication error."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            status_code=401,
            text="Unauthorized",
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await async_readeck_client.create_bookmark(url="https://example.com")

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_bookmark_forbidden_error(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test bookmark creation with forbidden error."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            status_code=403,
            text="Forbidden",
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await async_readeck_client.create_bookmark(url="https://example.com")

        assert exc_info.value.status_code == 403
        assert "Access forbidden" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_bookmark_validation_error(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test bookmark creation with validation error."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            status_code=422,
            json={"message": "Invalid URL format", "status": 422},
        )

        with pytest.raises(ReadeckValidationError) as exc_info:
            await async_readeck_client.create_bookmark(url="invalid-url")

        assert exc_info.value.status_code == 422
        assert "Validation error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_bookmark_server_error(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test bookmark creation with server error."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            status_code=500,
            text="Internal Server Error",
        )

        with pytest.raises(ReadeckServerError) as exc_info:
            await async_readeck_client.create_bookmark(url="https://example.com")

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_create_bookmark_invalid_json_response(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test bookmark creation with invalid JSON response."""
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            status_code=202,
            text="Invalid JSON response",
        )

        with pytest.raises(ReadeckError) as exc_info:
            await async_readeck_client.create_bookmark(url="https://example.com")

        assert "Failed to parse JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_bookmark_request_payload(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test that the request payload is correctly formatted."""
        expected_payload = {
            "url": "https://example.com/test",
            "title": "Test Title",
            "labels": ["test", "example"],
        }

        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
        )

        await async_readeck_client.create_bookmark(
            url="https://example.com/test",
            title="Test Title",
            labels=["test", "example"],
        )

        # Verify the request was made with correct payload
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path == "/api/bookmarks"
        assert request.headers["Content-Type"] == "application/json"

        # Check the request payload
        import json

        actual_payload = json.loads(request.content)
        assert actual_payload == expected_payload

    @pytest.mark.asyncio
    async def test_create_bookmark_request_payload_minimal(
        self, async_readeck_client: ReadeckClient, httpx_mock: HTTPXMock
    ):
        """Test that minimal request payload excludes None values."""
        expected_payload = {"url": "https://example.com", "labels": []}

        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://test.readeck.com/api/bookmarks",
            json={"message": "Bookmark created successfully", "status": 0},
            status_code=202,
        )

        await async_readeck_client.create_bookmark(url="https://example.com")

        # Verify the request was made with correct payload
        request = httpx_mock.get_request()

        # Check the request payload
        import json

        actual_payload = json.loads(request.content)
        assert actual_payload == expected_payload
        assert "title" not in actual_payload  # Should be excluded since it's None
