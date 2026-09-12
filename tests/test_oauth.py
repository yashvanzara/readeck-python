"""Tests for public Readeck OAuth support."""

import pytest
from pytest_httpx import HTTPXMock

from readeck import (
    DeviceAuthorization,
    OAuthClientRegistrationRequest,
    ReadeckOAuthClient,
    ReadeckOAuthError,
)


@pytest.mark.asyncio
async def test_info_and_metadata_use_public_instance_routes(httpx_mock: HTTPXMock):
    """OAuth discovery must not add the authenticated API prefix twice."""
    async with ReadeckOAuthClient("https://example.test/readeck/") as client:
        httpx_mock.add_response(
            url="https://example.test/readeck/api/info",
            json={
                "version": {"canonical": "1.0.0", "release": "1.0.0", "build": ""},
                "features": ["oauth"],
            },
        )
        httpx_mock.add_response(
            url="https://example.test/readeck/.well-known/oauth-authorization-server",
            json={
                "issuer": "https://example.test/readeck/",
                "token_endpoint": "https://example.test/readeck/api/oauth/token",
                "device_authorization_endpoint": "https://example.test/readeck/api/oauth/device",
            },
        )

        assert (await client.get_info()).supports_oauth is True
        metadata = await client.get_server_metadata()
        assert (
            str(metadata.token_endpoint)
            == "https://example.test/readeck/api/oauth/token"
        )


@pytest.mark.asyncio
async def test_register_client_and_start_device_authorization(httpx_mock: HTTPXMock):
    """Dynamic registration and device authorization send form-safe payloads."""
    async with ReadeckOAuthClient("https://example.test") as client:
        httpx_mock.add_response(
            method="POST",
            url="https://example.test/api/oauth/client",
            status_code=201,
            json={
                "client_id": "client-1",
                "client_name": "MCP client",
                "client_uri": "https://client.example/",
                "software_id": "io.example.mcp",
                "software_version": "1.0.0",
                "redirect_uris": [],
                "grant_types": ["urn:ietf:params:oauth:grant-type:device_code"],
                "response_types": [],
                "token_endpoint_auth_method": "none",
            },
        )
        httpx_mock.add_response(
            method="POST",
            url="https://example.test/api/oauth/device",
            json={
                "device_code": "device-code",
                "user_code": "USER-CODE",
                "verification_uri": "https://example.test/device",
                "verification_uri_complete": "https://example.test/device?user_code=USER-CODE",
                "expires_in": 600,
                "interval": 5,
            },
        )

        registration = await client.register_client(
            OAuthClientRegistrationRequest(
                client_name="MCP client",
                client_uri="https://client.example",
                software_id="io.example.mcp",
                software_version="1.0.0",
            )
        )
        authorization = await client.start_device_authorization(
            registration.client_id, "api:bookmarks:read"
        )

        assert registration.client_id == "client-1"
        assert authorization.user_code == "USER-CODE"


@pytest.mark.asyncio
async def test_poll_device_token_waits_and_handles_standard_errors(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
):
    """Polling retries pending responses and increases the interval on slow_down."""
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr("readeck.oauth.asyncio.sleep", fake_sleep)
    async with ReadeckOAuthClient("https://example.test") as client:
        httpx_mock.add_response(
            method="POST",
            url="https://example.test/api/oauth/token",
            status_code=400,
            json={"error": "authorization_pending"},
        )
        httpx_mock.add_response(
            method="POST",
            url="https://example.test/api/oauth/token",
            status_code=400,
            json={"error": "slow_down"},
        )
        httpx_mock.add_response(
            method="POST",
            url="https://example.test/api/oauth/token",
            status_code=201,
            json={
                "id": "token-id",
                "access_token": "secret-token",
                "token_type": "Bearer",
                "scope": "api:bookmarks:read",
            },
        )
        token = await client.poll_device_token(
            DeviceAuthorization(
                device_code="device-code",
                user_code="USER-CODE",
                verification_uri="https://example.test/device",
                verification_uri_complete="https://example.test/device?user_code=USER-CODE",
                expires_in=600,
                interval=2,
            ),
            "client",
        )

        assert token.id == "token-id"
        assert sleeps == [2, 7]


@pytest.mark.asyncio
async def test_oauth_errors_do_not_include_tokens(httpx_mock: HTTPXMock):
    """Protocol errors retain OAuth details without echoing submitted tokens."""
    async with ReadeckOAuthClient("https://example.test") as client:
        httpx_mock.add_response(
            method="POST",
            url="https://example.test/api/oauth/token",
            status_code=400,
            json={"error": "invalid_grant", "error_description": "invalid device code"},
        )

        with pytest.raises(ReadeckOAuthError) as exc_info:
            await client.poll_device_token(
                DeviceAuthorization(
                    device_code="do-not-leak",
                    user_code="USER-CODE",
                    verification_uri="https://example.test/device",
                    verification_uri_complete="https://example.test/device?user_code=USER-CODE",
                    expires_in=600,
                ),
                "client",
            )
        assert "do-not-leak" not in str(exc_info.value)


@pytest.mark.asyncio
async def test_revoke_token_uses_bearer_authorization(httpx_mock: HTTPXMock):
    """Revocation requires the submitted token as Readeck bearer authentication."""
    async with ReadeckOAuthClient("https://example.test") as client:
        httpx_mock.add_response(
            method="POST", url="https://example.test/api/oauth/revoke", json={}
        )
        await client.revoke_token("secret-token")
        request = httpx_mock.get_requests()[0]
        assert request.headers["Authorization"] == "Bearer secret-token"
