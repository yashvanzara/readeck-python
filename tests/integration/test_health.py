"""Live health and profile checks."""

import pytest

from readeck import ReadeckClient

from .helpers import ReadeckCredentials

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_health_check(readeck_client: ReadeckClient) -> None:
    assert await readeck_client.health_check() is True


@pytest.mark.asyncio
async def test_get_user_profile(
    readeck_client: ReadeckClient, readeck_credentials: ReadeckCredentials
) -> None:
    profile = await readeck_client.get_user_profile()
    assert profile.user.username == readeck_credentials.username
    assert profile.user.email == "itest@example.com"
