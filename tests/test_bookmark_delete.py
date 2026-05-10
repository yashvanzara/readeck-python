"""Tests for bookmark delete functionality."""

import pytest
from pytest_httpx import HTTPXMock

from readeck import ReadeckClient
from readeck.exceptions import ReadeckAuthError, ReadeckError, ReadeckNotFoundError


@pytest.mark.asyncio
async def test_delete_bookmark_success(httpx_mock: HTTPXMock):
    """Test successful bookmark deletion returns None."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.example.com/api/bookmarks/abc123",
            status_code=204,
        )

        result = await client.delete_bookmark("abc123")
        assert result is None


@pytest.mark.asyncio
async def test_delete_bookmark_not_found(httpx_mock: HTTPXMock):
    """Test bookmark not found error."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.example.com/api/bookmarks/nonexistent",
            status_code=404,
        )

        with pytest.raises(ReadeckNotFoundError) as exc_info:
            await client.delete_bookmark("nonexistent")

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_delete_bookmark_unauthorized(httpx_mock: HTTPXMock):
    """Test unauthorized access error."""
    async with ReadeckClient("https://api.example.com", "invalid-token") as client:
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.example.com/api/bookmarks/abc123",
            status_code=401,
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await client.delete_bookmark("abc123")

        assert exc_info.value.status_code == 401
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_delete_bookmark_forbidden(httpx_mock: HTTPXMock):
    """Test forbidden access error."""
    async with ReadeckClient("https://api.example.com", "limited-token") as client:
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.example.com/api/bookmarks/restricted",
            status_code=403,
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await client.delete_bookmark("restricted")

        assert exc_info.value.status_code == 403
        assert "forbidden" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_delete_bookmark_server_error(httpx_mock: HTTPXMock):
    """Test handling of server errors."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.example.com/api/bookmarks/abc123",
            status_code=500,
            text="Internal Server Error",
        )

        with pytest.raises(ReadeckError) as exc_info:
            await client.delete_bookmark("abc123")

        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_delete_bookmark_url_construction(httpx_mock: HTTPXMock):
    """Test that the correct URL is constructed for bookmark deletion."""
    bookmark_id = "test-bookmark-123"

    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="DELETE",
            url=f"https://api.example.com/api/bookmarks/{bookmark_id}",  # noqa: E231
            status_code=204,
        )

        result = await client.delete_bookmark(bookmark_id)
        assert result is None
