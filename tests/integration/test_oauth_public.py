"""Live public OAuth discovery and client registration."""

import pytest

from readeck import OAuthClientRegistrationRequest, ReadeckOAuthClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_info_and_server_metadata(
    readeck_oauth_client: ReadeckOAuthClient,
) -> None:
    info = await readeck_oauth_client.get_info()
    assert info.version.canonical
    if not info.supports_oauth:
        pytest.skip("Readeck instance does not advertise OAuth")

    metadata = await readeck_oauth_client.get_server_metadata()
    assert str(metadata.token_endpoint).endswith("/api/oauth/token")


@pytest.mark.asyncio
async def test_register_public_client(readeck_oauth_client: ReadeckOAuthClient) -> None:
    info = await readeck_oauth_client.get_info()
    if not info.supports_oauth:
        pytest.skip("Readeck instance does not advertise OAuth")

    registration = await readeck_oauth_client.register_client(
        OAuthClientRegistrationRequest(
            client_name="readeck-python-itest",
            client_uri="https://example.com",
            software_id="io.github.yashvanzara.readeck-python",
            software_version="0.3.1",
        )
    )
    assert registration.client_id
    assert registration.client_name == "readeck-python-itest"
