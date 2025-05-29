"""Test fixtures and utilities."""

from typing import Any, AsyncGenerator, Dict

import pytest

from readeck import ReadeckClient


@pytest.fixture
def mock_user_profile_data() -> Dict[str, Any]:
    """Mock user profile response data."""
    return {
        "provider": {
            "application": "readeck",
            "id": "tok_12345",
            "name": "Local Provider",
            "permissions": ["read", "write"],
            "roles": ["user"],
        },
        "user": {
            "created": "2024-01-01T10:00:00Z",
            "email": "test@example.com",
            "updated": "2024-12-01T15:30:00Z",
            "username": "testuser",
            "settings": {
                "debug_info": False,
                "reader_settings": {
                    "font": "Arial",
                    "font_size": 16,
                    "line_height": 24,
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
