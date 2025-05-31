"""Tests for bookmark export functionality."""

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


class TestBookmarkExport:
    """Test bookmark export functionality."""

    @pytest.mark.asyncio
    async def test_export_bookmark_markdown_success(self, httpx_mock: HTTPXMock):
        """Test successful bookmark export in markdown format."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"
        markdown_content = """# Example Article

This is a test article exported from Readeck.

## Section 1

Some content here.

## Section 2

More content here.
"""

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text=markdown_content,
            status_code=200,
            headers={"Content-Type": "text/markdown; charset=utf-8"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark(bookmark_id, format="md")

        assert isinstance(result, str)
        assert result == markdown_content
        assert "# Example Article" in result

    @pytest.mark.asyncio
    async def test_export_bookmark_epub_success(self, httpx_mock: HTTPXMock):
        """Test successful bookmark export in EPUB format."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"
        epub_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Mock EPUB binary data

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.epub",  # noqa: E231
            content=epub_content,
            status_code=200,
            headers={"Content-Type": "application/epub+zip"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark(bookmark_id, format="epub")

        assert isinstance(result, bytes)
        assert result == epub_content

    @pytest.mark.asyncio
    async def test_export_bookmark_default_format(self, httpx_mock: HTTPXMock):
        """Test that default format is markdown."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"
        markdown_content = "# Default Format Test"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text=markdown_content,
            status_code=200,
            headers={"Content-Type": "text/markdown; charset=utf-8"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        # Test without specifying format (should default to "md")
        result = await client.export_bookmark(bookmark_id)

        assert isinstance(result, str)
        assert result == markdown_content

    @pytest.mark.asyncio
    async def test_export_bookmark_invalid_format(self):
        """Test export with invalid format."""
        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        with pytest.raises(ReadeckValidationError) as exc_info:
            await client.export_bookmark("test_id", format="pdf")

        assert "Invalid format 'pdf'" in str(exc_info.value)
        assert "Allowed formats: md, epub" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_bookmark_not_found(self, httpx_mock: HTTPXMock):
        """Test export when bookmark is not found."""
        bookmark_id = "nonexistent_id"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            status_code=404,
            text="Bookmark not found",
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        with pytest.raises(ReadeckNotFoundError) as exc_info:
            await client.export_bookmark(bookmark_id, format="md")

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_bookmark_auth_error_401(self, httpx_mock: HTTPXMock):
        """Test export with authentication error (401)."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            status_code=401,
            text="Unauthorized",
        )

        client = ReadeckClient(
            base_url="https://test.readeck.com", token="invalid_token"
        )

        with pytest.raises(ReadeckAuthError) as exc_info:
            await client.export_bookmark(bookmark_id, format="md")

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_bookmark_auth_error_403(self, httpx_mock: HTTPXMock):
        """Test export with forbidden error (403)."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            status_code=403,
            text="Forbidden",
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        with pytest.raises(ReadeckAuthError) as exc_info:
            await client.export_bookmark(bookmark_id, format="md")

        assert exc_info.value.status_code == 403
        assert "Access forbidden" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_bookmark_server_error(self, httpx_mock: HTTPXMock):
        """Test export with server error (500)."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            status_code=500,
            text="Internal Server Error",
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        with pytest.raises(ReadeckServerError) as exc_info:
            await client.export_bookmark(bookmark_id, format="md")

        assert exc_info.value.status_code == 500
        assert "Server error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_bookmark_generic_error(self, httpx_mock: HTTPXMock):
        """Test export with generic HTTP error."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            status_code=400,
            text="Bad Request",
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        with pytest.raises(ReadeckError) as exc_info:
            await client.export_bookmark(bookmark_id, format="md")

        assert exc_info.value.status_code == 400
        assert "HTTP 400" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_bookmark_correct_headers_markdown(
        self, httpx_mock: HTTPXMock
    ):
        """Test that correct Accept header is sent for markdown format."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text="# Test",
            status_code=200,
            match_headers={"Accept": "text/markdown"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")
        await client.export_bookmark(bookmark_id, format="md")

    @pytest.mark.asyncio
    async def test_export_bookmark_correct_headers_epub(self, httpx_mock: HTTPXMock):
        """Test that correct Accept header is sent for EPUB format."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.epub",  # noqa: E231
            content=b"epub_content",
            status_code=200,
            match_headers={"Accept": "application/epub+zip"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")
        await client.export_bookmark(bookmark_id, format="epub")

    @pytest.mark.asyncio
    async def test_export_bookmark_url_construction(self, httpx_mock: HTTPXMock):
        """Test that the URL is constructed correctly."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        # Test markdown URL construction
        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text="# Test",
            status_code=200,
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")
        await client.export_bookmark(bookmark_id, format="md")

        # Test EPUB URL construction
        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.epub",  # noqa: E231
            content=b"epub_content",
            status_code=200,
        )

        await client.export_bookmark(bookmark_id, format="epub")

    @pytest.mark.asyncio
    async def test_export_bookmark_empty_content(self, httpx_mock: HTTPXMock):
        """Test export with empty content."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text="",
            status_code=200,
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark(bookmark_id, format="md")

        assert isinstance(result, str)
        assert result == ""

    @pytest.mark.asyncio
    async def test_export_bookmark_large_content(self, httpx_mock: HTTPXMock):
        """Test export with large content."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"
        large_content = "# Large Article\n\n" + "Lorem ipsum dolor sit amet. " * 1000

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text=large_content,
            status_code=200,
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark(bookmark_id, format="md")

        assert isinstance(result, str)
        assert len(result) > 20000  # Should be a large string
        assert result.startswith("# Large Article")
