"""Tests for bookmark updates and label listing."""

import json

import pytest
from pytest_httpx import HTTPXMock

from readeck import BookmarkUpdateRequest, ReadeckClient


@pytest.mark.asyncio
async def test_update_bookmark(httpx_mock: HTTPXMock):
    """Bookmark updates use PATCH and omit fields that were not provided."""
    async with ReadeckClient("https://example.test/readeck", "token") as client:
        httpx_mock.add_response(
            method="PATCH",
            url="https://example.test/readeck/api/bookmarks/bookmark-id",
            json={"href": "https://example.test/readeck/api/bookmarks/bookmark-id"},
        )
        result = await client.update_bookmark(
            "bookmark-id", BookmarkUpdateRequest(title="Updated")
        )
        assert result.href.endswith("bookmark-id")
        assert json.loads(httpx_mock.get_requests()[0].content) == {"title": "Updated"}


@pytest.mark.asyncio
async def test_get_labels(httpx_mock: HTTPXMock):
    """Label listing returns typed label data."""
    async with ReadeckClient("https://example.test", "token") as client:
        httpx_mock.add_response(
            url="https://example.test/api/bookmarks/labels",
            json=[
                {
                    "name": "reading",
                    "count": 3,
                    "href": "https://example.test/api/bookmarks/labels?name=reading",
                    "href_bookmarks": "https://example.test/api/bookmarks?labels=reading",
                }
            ],
        )
        labels = await client.get_labels()
        assert labels[0].name == "reading"
        assert labels[0].count == 3
