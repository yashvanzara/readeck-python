"""Test fixtures and utilities."""

from typing import Any, AsyncGenerator, Dict

import pytest

from readeck import ReadeckClient


@pytest.fixture
def mock_user_profile_data() -> Dict[str, Any]:
    """Mock user profile response data."""
    return {
        "provider": {
            "name": "http session",
            "id": "",
            "application": "",
            "roles": ["admin"],
            "permissions": [
                "api:admin:users:read",
                "api:admin:users:write",
                "api:bookmarks:collections:read",
                "api:bookmarks:collections:write",
                "api:bookmarks:export",
                "api:bookmarks:read",
                "api:bookmarks:write",
                "api:opds:read",
                "api:profile:read",
                "api:profile:tokens:delete",
            ],
        },
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "created": "2024-10-30T18:20:59.12323Z",
            "updated": "2024-11-09T14:09:50.231744Z",
            "settings": {
                "debug_info": False,
                "lang": "en-US",
                "addon_reminder": True,
                "email_settings": {"reply_to": "", "epub_to": ""},
                "reader_settings": {
                    "width": 0,
                    "font": "lora",
                    "font_size": 2,
                    "line_height": 2,
                    "justify": 0,
                    "hyphenation": 0,
                },
            },
        },
    }


@pytest.fixture
def readeck_client() -> ReadeckClient:
    """Create a Readeck client instance for testing."""
    return ReadeckClient(base_url="https://test.readeck.com", token="test_token_12345")


@pytest.fixture
async def async_readeck_client() -> AsyncGenerator[ReadeckClient, None]:
    """Create an async Readeck client instance for testing."""
    client = ReadeckClient(
        base_url="https://test.readeck.com", token="test_token_12345"
    )
    yield client
    await client.close()


@pytest.fixture
def mock_bookmark_data() -> Dict[str, Any]:
    """Mock bookmark response data."""
    return {
        "id": "abc123",
        "href": "https://example.com/article",
        "url": "https://example.com/article",
        "title": "Example Article",
        "description": "An example article about programming",
        "site": "example.com",
        "site_name": "Example Site",
        "authors": ["John Doe"],
        "type": "article",
        "document_type": "text/html",
        "lang": "en",
        "text_direction": "ltr",
        "loaded": True,
        "has_article": True,
        "is_archived": False,
        "is_deleted": False,
        "is_marked": False,
        "word_count": 1500,
        "reading_time": 6,
        "read_progress": 0.0,
        "state": 0,
        "labels": ["programming", "tutorial"],
        "created": "2024-01-15T10:30:00.000Z",
        "updated": "2024-01-15T10:30:00.000Z",
        "published": "2024-01-15T08:00:00.000Z",
        "resources": {
            "article": {"src": "https://example.com/article/content"},
            "icon": {
                "src": "https://example.com/favicon.ico",
                "height": 32,
                "width": 32,
            },
            "image": {
                "src": "https://example.com/article/hero.jpg",
                "height": 600,
                "width": 1200,
            },
            "thumbnail": {
                "src": "https://example.com/article/thumb.jpg",
                "height": 300,
                "width": 600,
            },
        },
    }
