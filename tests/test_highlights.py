"""Tests for the Readeck highlights functionality."""

from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from readeck.exceptions import ReadeckAuthError, ReadeckServerError
from readeck.models import Highlight, HighlightListResponse


@pytest.fixture
def mock_highlight_data() -> list[dict]:
    """Fixture for mock highlight data."""
    return [
        {
            "id": "highlight1",
            "href": "https://api.readeck.com/bookmarks/annotations/highlight1",
            "bookmark_id": "bookmark1",
            "bookmark_href": "https://api.readeck.com/bookmarks/bookmark1",
            "bookmark_title": "Test Bookmark",
            "bookmark_url": "https://example.com/test",
            "bookmark_site_name": "Example",
            "text": "This is a test highlight",
            "created": "2025-01-01T12:00:00Z",
            "updated": "2025-01-01T12:00:00Z",
        },
        {
            "id": "highlight2",
            "href": "https://api.readeck.com/bookmarks/annotations/highlight2",
            "bookmark_id": "bookmark2",
            "bookmark_href": "https://api.readeck.com/bookmarks/bookmark2",
            "bookmark_title": "Another Bookmark",
            "bookmark_url": "https://example.com/another",
            "bookmark_site_name": "Example",
            "text": "Another test highlight",
            "created": "2025-01-02T12:00:00Z",
            "updated": "2025-01-02T12:00:00Z",
        },
    ]


class TestGetHighlights:
    """Test get_highlights method."""

    @pytest.mark.asyncio
    async def test_get_highlights_success(
        self, async_readeck_client, mock_highlight_data, httpx_mock: HTTPXMock
    ):
        """Test successful retrieval of highlights."""
        # Mock the HTTP response
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            json=mock_highlight_data,
            status_code=200,
            headers={
                "Total-Count": "2",
                "Current-Page": "1",
                "Total-Pages": "1",
                "Link": (
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="first", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="last"'
                ),
            },
        )

        # Manually set the last_response on the client to simulate what should happen in the real client
        async_readeck_client._client.last_response = {
            "headers": {
                "Total-Count": "2",
                "Current-Page": "1",
                "Total-Pages": "1",
                "Link": (
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="first", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="last"'
                ),
            }
        }

        # Call the method
        response = await async_readeck_client.get_highlights()

        # Assert the response is correct
        assert isinstance(response, HighlightListResponse)
        assert len(response.items) == 2
        assert response.total_count == 2
        assert response.page == 1
        assert response.total_pages == 1

        # Now we can test the pagination links parsing
        assert response.links
        assert "first" in response.links
        assert "last" in response.links
        assert (
            response.links["first"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=1"
        )
        assert (
            response.links["last"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=1"
        )

        # Verify the highlights were parsed correctly
        highlight = response.items[0]
        assert isinstance(highlight, Highlight)
        assert highlight.id == "highlight1"
        assert highlight.text == "This is a test highlight"
        assert highlight.bookmark_title == "Test Bookmark"
        assert highlight.bookmark_url == "https://example.com/test"
        assert highlight.bookmark_site_name == "Example"
        assert highlight.created == datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert highlight.updated == datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    @pytest.mark.asyncio
    async def test_get_highlights_with_pagination(
        self, async_readeck_client, mock_highlight_data, httpx_mock: HTTPXMock
    ):
        """Test retrieving highlights with pagination parameters."""
        # Mock the HTTP response with only the second highlight
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations?limit=1&offset=1",
            json=mock_highlight_data[1:2],
            status_code=200,
            headers={
                "Total-Count": "2",
                "Current-Page": "2",
                "Total-Pages": "2",
                "Link": (
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="prev", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=2>; rel="last"'
                ),
            },
        )

        # Manually set the last_response on the client to simulate what should happen in the real client
        async_readeck_client._client.last_response = {
            "headers": {
                "Total-Count": "2",
                "Current-Page": "2",
                "Total-Pages": "2",
                "Link": (
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="prev", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=2>; rel="last"'
                ),
            }
        }

        # Call the method with pagination parameters
        response = await async_readeck_client.get_highlights(limit=1, offset=1)

        # Assert the response is correct
        assert len(response.items) == 1
        assert response.items[0].id == "highlight2"
        assert response.total_count == 2  # From Total-Count header
        assert response.page == 2  # From Current-Page header
        assert response.total_pages == 2  # From Total-Pages header

        # Test the pagination links parsing
        assert response.links
        assert "prev" in response.links
        assert "last" in response.links
        assert (
            response.links["prev"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=1"
        )
        assert (
            response.links["last"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=2"
        )

    @pytest.mark.asyncio
    async def test_get_highlights_auth_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test authentication error when getting highlights."""
        # Mock HTTP response with 401 status
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            status_code=401,
            json={"message": "Unauthorized", "status": 401},
        )

        # Verify the correct exception is raised
        with pytest.raises(
            ReadeckAuthError, match="Authentication failed. Please check your token."
        ):
            await async_readeck_client.get_highlights()

    @pytest.mark.asyncio
    async def test_get_highlights_forbidden_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test forbidden error when getting highlights."""
        # Mock HTTP response with 403 status
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            status_code=403,
            json={"message": "Forbidden", "status": 403},
        )

        # Verify the correct exception is raised - the client.py code raises ReadeckAuthError with a specific message
        with pytest.raises(
            ReadeckAuthError, match="Access forbidden. Insufficient permissions."
        ):
            await async_readeck_client.get_highlights()

    @pytest.mark.asyncio
    async def test_get_highlights_server_error(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test server error when getting highlights."""
        # Mock HTTP response with 500 status
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            status_code=500,
            json={"message": "Internal Server Error", "status": 500},
        )

        # Verify the correct exception is raised - the client.py code raises ReadeckServerError with a specific message
        with pytest.raises(ReadeckServerError, match="Server error:"):
            await async_readeck_client.get_highlights()

    @pytest.mark.asyncio
    async def test_get_highlights_invalid_response(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test handling of invalid response format."""
        # Mock HTTP response with invalid data (missing required fields)
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            json=[{"id": "1"}],  # Missing required fields
            status_code=200,
            headers={},
        )

        # This should raise a ValidationError from pydantic
        with pytest.raises(Exception):
            await async_readeck_client.get_highlights()

    @pytest.mark.asyncio
    async def test_get_highlights_missing_updated_field(
        self, async_readeck_client, httpx_mock: HTTPXMock
    ):
        """Test handling of highlights with missing 'updated' field."""
        # Mock data without the 'updated' field (which can happen in real API responses)
        mock_data_no_updated = [
            {
                "id": "highlight1",
                "href": "https://api.readeck.com/bookmarks/annotations/highlight1",
                "bookmark_id": "bookmark1",
                "bookmark_href": "https://api.readeck.com/bookmarks/bookmark1",
                "bookmark_title": "Test Bookmark",
                "bookmark_url": "https://example.com/test",
                "bookmark_site_name": "Example",
                "text": "This is a test highlight",
                "created": "2025-01-01T12:00:00Z",
                # Note: No 'updated' field
            }
        ]

        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            json=mock_data_no_updated,
            status_code=200,
            headers={
                "Total-Count": "1",
                "Current-Page": "1",
                "Total-Pages": "1",
            },
        )

        async_readeck_client._client.last_response = {
            "headers": {
                "Total-Count": "1",
                "Current-Page": "1",
                "Total-Pages": "1",
            }
        }

        # This should not raise an exception and should handle missing 'updated' field gracefully
        response = await async_readeck_client.get_highlights()

        assert len(response.items) == 1
        highlight = response.items[0]
        assert highlight.id == "highlight1"
        assert highlight.text == "This is a test highlight"
        assert (
            highlight.updated is None
        )  # Should be None when missing from API response
        assert highlight.created == datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    @pytest.mark.asyncio
    async def test_get_highlights_no_headers(
        self, async_readeck_client, mock_highlight_data, httpx_mock: HTTPXMock
    ):
        """Test highlights with no pagination headers (fallback behavior)."""
        # Mock HTTP response without pagination headers
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            json=mock_highlight_data,
            status_code=200,
            headers={},
        )

        # No last_response set, should fall back to defaults
        async_readeck_client._client.last_response = {"headers": {}}

        response = await async_readeck_client.get_highlights()

        # Should use fallback values
        assert len(response.items) == 2
        assert response.total_count == 2  # Fallback to len(items)
        assert response.page == 1  # Fallback to 1
        assert response.total_pages == 1  # Fallback to 1
        assert response.links == {}  # No links when no Link header

    @pytest.mark.asyncio
    async def test_get_highlights_complex_link_header(
        self, async_readeck_client, mock_highlight_data, httpx_mock: HTTPXMock
    ):
        """Test parsing of complex Link header with multiple relationships."""
        # Mock HTTP response with complex Link header
        httpx_mock.add_response(
            method="GET",
            url="https://test.readeck.com/api/bookmarks/annotations",
            json=mock_highlight_data,
            status_code=200,
            headers={
                "Total-Count": "10",
                "Current-Page": "3",
                "Total-Pages": "5",
                "Link": (
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="first", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=2>; rel="prev", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=4>; rel="next", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=5>; rel="last"'
                ),
            },
        )

        # Set the headers on the client
        async_readeck_client._client.last_response = {
            "headers": {
                "Total-Count": "10",
                "Current-Page": "3",
                "Total-Pages": "5",
                "Link": (
                    '<https://test.readeck.com/api/bookmarks/annotations?page=1>; rel="first", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=2>; rel="prev", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=4>; rel="next", '
                    '<https://test.readeck.com/api/bookmarks/annotations?page=5>; rel="last"'
                ),
            }
        }

        response = await async_readeck_client.get_highlights()

        # Test all pagination aspects
        assert response.total_count == 10
        assert response.page == 3
        assert response.total_pages == 5

        # Test all link relationships
        assert len(response.links) == 4
        assert (
            response.links["first"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=1"
        )
        assert (
            response.links["prev"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=2"
        )
        assert (
            response.links["next"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=4"
        )
        assert (
            response.links["last"]
            == "https://test.readeck.com/api/bookmarks/annotations?page=5"
        )
