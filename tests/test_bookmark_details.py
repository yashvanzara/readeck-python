"""Tests for bookmark details functionality."""

import pytest
from pytest_httpx import HTTPXMock

from readeck import ReadeckClient
from readeck.exceptions import ReadeckAuthError, ReadeckError, ReadeckNotFoundError


@pytest.fixture
def mock_bookmark_details_response():
    """Mock response for bookmark details."""
    return {
        "id": "abc123",
        "href": "https://example.com/article",
        "url": "https://example.com/article",
        "title": "Example Article",
        "description": "This is an example article description",
        "site": "example.com",
        "site_name": "Example Site",
        "authors": ["John Doe", "Jane Smith"],
        "type": "article",
        "document_type": "html",
        "lang": "en",
        "text_direction": "ltr",
        "loaded": True,
        "has_article": True,
        "is_archived": False,
        "is_deleted": False,
        "is_marked": True,
        "word_count": 1500,
        "reading_time": 6,
        "read_progress": 0.3,
        "state": 1,
        "labels": ["tech", "programming"],
        "created": "2024-01-15T10:30:00.000Z",
        "updated": "2024-01-15T11:00:00.000Z",
        "published": "2024-01-15T09:00:00.000Z",
        "resources": {
            "article": {"src": "https://example.com/api/bookmarks/abc123/article"},
            "icon": {
                "src": "https://example.com/favicon.ico",
                "height": 32,
                "width": 32,
            },
            "image": {
                "src": "https://example.com/image.jpg",
                "height": 400,
                "width": 600,
            },
            "thumbnail": {
                "src": "https://example.com/thumb.jpg",
                "height": 200,
                "width": 300,
            },
        },
        "links": [
            {
                "content_type": "text/html",
                "domain": "github.com",
                "is_page": True,
                "title": "GitHub Repository",
                "url": "https://github.com/example/repo",
            },
            {
                "content_type": "application/pdf",
                "domain": "example.com",
                "is_page": False,
                "title": "Related Document",
                "url": "https://example.com/document.pdf",
            },
        ],
        "read_anchor": "chapter-3-introduction",
    }


@pytest.mark.asyncio
async def test_get_bookmark_success(
    mock_bookmark_details_response, httpx_mock: HTTPXMock
):
    """Test successful bookmark details retrieval."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/abc123",
            json=mock_bookmark_details_response,
            status_code=200,
        )

        bookmark = await client.get_bookmark("abc123")

        # Verify basic bookmark properties
        assert bookmark.id == "abc123"
        assert bookmark.title == "Example Article"
        assert bookmark.description == "This is an example article description"
        assert bookmark.href == "https://example.com/article"
        assert bookmark.url == "https://example.com/article"
        assert bookmark.site == "example.com"
        assert bookmark.site_name == "Example Site"
        assert bookmark.type == "article"
        assert bookmark.document_type == "html"
        assert bookmark.lang == "en"
        assert bookmark.text_direction == "ltr"

        # Verify state flags
        assert bookmark.loaded is True
        assert bookmark.has_article is True
        assert bookmark.is_archived is False
        assert bookmark.is_deleted is False
        assert bookmark.is_marked is True

        # Verify content metadata
        assert bookmark.word_count == 1500
        assert bookmark.reading_time == 6
        assert bookmark.read_progress == 0.3
        assert bookmark.state == 1

        # Verify authors and labels
        assert bookmark.authors == ["John Doe", "Jane Smith"]
        assert bookmark.labels == ["tech", "programming"]

        # Verify timestamps
        assert bookmark.created.year == 2024
        assert bookmark.created.month == 1
        assert bookmark.created.day == 15
        assert bookmark.updated.year == 2024
        assert bookmark.published is not None

        # Verify resources
        assert bookmark.resources is not None
        assert bookmark.resources.article is not None
        assert (
            bookmark.resources.article.src
            == "https://example.com/api/bookmarks/abc123/article"
        )
        assert bookmark.resources.icon is not None
        assert bookmark.resources.icon.height == 32
        assert bookmark.resources.icon.width == 32
        assert bookmark.resources.image is not None
        assert bookmark.resources.image.height == 400
        assert bookmark.resources.image.width == 600

        # Verify links (new fields)
        assert bookmark.links is not None
        assert len(bookmark.links) == 2

        first_link = bookmark.links[0]
        assert first_link.content_type == "text/html"
        assert first_link.domain == "github.com"
        assert first_link.is_page is True
        assert first_link.title == "GitHub Repository"
        assert first_link.url == "https://github.com/example/repo"

        second_link = bookmark.links[1]
        assert second_link.content_type == "application/pdf"
        assert second_link.domain == "example.com"
        assert second_link.is_page is False
        assert second_link.title == "Related Document"
        assert second_link.url == "https://example.com/document.pdf"

        # Verify read anchor
        assert bookmark.read_anchor == "chapter-3-introduction"


@pytest.mark.asyncio
async def test_get_bookmark_minimal_response(httpx_mock: HTTPXMock):
    """Test bookmark details with minimal required fields only."""
    minimal_response = {
        "id": "min123",
        "href": "https://minimal.com",
        "url": "https://minimal.com",
        "title": "Minimal Bookmark",
        "type": "article",
        "created": "2024-01-15T10:30:00.000Z",
        "updated": "2024-01-15T11:00:00.000Z",
    }

    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/min123",
            json=minimal_response,
            status_code=200,
        )

        bookmark = await client.get_bookmark("min123")

        # Verify required fields
        assert bookmark.id == "min123"
        assert bookmark.title == "Minimal Bookmark"
        assert bookmark.href == "https://minimal.com"
        assert bookmark.type == "article"

        # Verify optional fields have defaults
        assert bookmark.description == ""
        assert bookmark.labels == []
        assert bookmark.authors == []
        assert bookmark.loaded is False
        assert bookmark.has_article is False
        assert bookmark.is_archived is False
        assert bookmark.is_deleted is False
        assert bookmark.is_marked is False
        assert bookmark.word_count == 0
        assert bookmark.reading_time == 0
        assert bookmark.read_progress == 0.0
        assert bookmark.state == 0
        assert bookmark.resources is None
        assert bookmark.links is None
        assert bookmark.read_anchor is None


@pytest.mark.asyncio
async def test_get_bookmark_not_found(httpx_mock: HTTPXMock):
    """Test bookmark not found error."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/nonexistent",
            status_code=404,
        )

        with pytest.raises(ReadeckNotFoundError) as exc_info:
            await client.get_bookmark("nonexistent")

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_bookmark_unauthorized(httpx_mock: HTTPXMock):
    """Test unauthorized access error."""
    async with ReadeckClient("https://api.example.com", "invalid-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/abc123",
            status_code=401,
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await client.get_bookmark("abc123")

        assert exc_info.value.status_code == 401
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_bookmark_forbidden(httpx_mock: HTTPXMock):
    """Test forbidden access error."""
    async with ReadeckClient("https://api.example.com", "limited-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/restricted",
            status_code=403,
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await client.get_bookmark("restricted")

        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_bookmark_invalid_json(httpx_mock: HTTPXMock):
    """Test handling of invalid JSON response."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/abc123",
            text="invalid json",
            status_code=200,
        )

        with pytest.raises(ReadeckError) as exc_info:
            await client.get_bookmark("abc123")

        assert "failed to parse json" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_bookmark_malformed_response(httpx_mock: HTTPXMock):
    """Test handling of malformed response structure."""
    malformed_response = {
        "id": "abc123",
        # Missing required fields like href, url, title, type, created, updated
    }

    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/abc123",
            json=malformed_response,
            status_code=200,
        )

        with pytest.raises(ReadeckError) as exc_info:
            await client.get_bookmark("abc123")

        assert "failed to parse bookmark response" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_bookmark_server_error(httpx_mock: HTTPXMock):
    """Test handling of server errors."""
    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/bookmarks/abc123",
            status_code=500,
            text="Internal Server Error",
        )

        with pytest.raises(ReadeckError) as exc_info:
            await client.get_bookmark("abc123")

        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_bookmark_url_construction(httpx_mock: HTTPXMock):
    """Test that the correct URL is constructed for bookmark details."""
    bookmark_id = "test-bookmark-123"

    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url=f"https://api.example.com/api/bookmarks/{bookmark_id}",  # noqa: E231
            json={
                "id": bookmark_id,
                "href": "https://example.com",
                "url": "https://example.com",
                "title": "Test",
                "type": "article",
                "created": "2024-01-15T10:30:00.000Z",
                "updated": "2024-01-15T11:00:00.000Z",
            },
            status_code=200,
        )

        bookmark = await client.get_bookmark(bookmark_id)
        assert bookmark.id == bookmark_id


@pytest.mark.asyncio
async def test_get_bookmark_with_special_characters(httpx_mock: HTTPXMock):
    """Test bookmark ID with special characters (URL encoding)."""
    bookmark_id = "bookmark-with_special.chars"

    async with ReadeckClient("https://api.example.com", "test-token") as client:
        httpx_mock.add_response(
            method="GET",
            url=f"https://api.example.com/api/bookmarks/{bookmark_id}",  # noqa: E231
            json={
                "id": bookmark_id,
                "href": "https://example.com",
                "url": "https://example.com",
                "title": "Special Chars Test",
                "type": "article",
                "created": "2024-01-15T10:30:00.000Z",
                "updated": "2024-01-15T11:00:00.000Z",
            },
            status_code=200,
        )

        bookmark = await client.get_bookmark(bookmark_id)
        assert bookmark.id == bookmark_id
        assert bookmark.title == "Special Chars Test"
