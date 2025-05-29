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
