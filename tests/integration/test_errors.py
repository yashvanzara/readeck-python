"""Live error-path coverage."""

import pytest

from readeck import ReadeckClient
from readeck.exceptions import ReadeckAuthError, ReadeckNotFoundError

from .helpers import ReadeckCredentials

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_invalid_token_raises_auth_error(
    readeck_credentials: ReadeckCredentials,
) -> None:
    async with ReadeckClient(
        base_url=readeck_credentials.base_url, token="not-a-real-token"
    ) as client:
        with pytest.raises(ReadeckAuthError):
            await client.get_user_profile()


@pytest.mark.asyncio
async def test_missing_bookmark_raises_not_found(
    readeck_client: ReadeckClient,
) -> None:
    with pytest.raises(ReadeckNotFoundError):
        await readeck_client.get_bookmark("does-not-exist")
