"""OAuth 2.0 support for Readeck instances."""

import asyncio
import time
from typing import Any

import httpx
from pydantic import ValidationError

from .exceptions import (
    ReadeckError,
    ReadeckOAuthError,
    ReadeckOAuthPendingError,
    ReadeckOAuthSlowDownError,
)
from .models import (
    DeviceAuthorization,
    OAuthClientRegistration,
    OAuthClientRegistrationRequest,
    OAuthServerMetadata,
    OAuthToken,
    ReadeckInfo,
)

DEVICE_CODE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"


class ReadeckOAuthClient:
    """Async client for Readeck's public OAuth and instance endpoints.

    This client intentionally keeps no token state. Callers are responsible for
    retaining any token returned by :meth:`poll_device_token`.
    """

    def __init__(
        self, base_url: str, timeout: float = 30.0, **httpx_kwargs: Any
    ) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Accept": "application/json", "User-Agent": "readeck-python/0.2.0"}
        if "headers" in httpx_kwargs:
            headers.update(httpx_kwargs.pop("headers"))
        self._client = httpx.AsyncClient(
            base_url=self.base_url, headers=headers, timeout=timeout, **httpx_kwargs
        )

    async def __aenter__(self) -> "ReadeckOAuthClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _oauth_error(response: httpx.Response) -> ReadeckOAuthError:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not isinstance(data, dict) or not isinstance(data.get("error"), str):
            return ReadeckOAuthError("oauth_error", status_code=response.status_code)
        error = data["error"]
        description = data.get("error_description")
        uri = data.get("error_uri")
        if not isinstance(description, str):
            description = None
        if not isinstance(uri, str):
            uri = None
        error_type = {
            "authorization_pending": ReadeckOAuthPendingError,
            "slow_down": ReadeckOAuthSlowDownError,
        }.get(error, ReadeckOAuthError)
        return error_type(error, description, uri, response.status_code)

    async def _request_json(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = await self._client.request(method, self._url(path), **kwargs)
        except httpx.TimeoutException as exc:
            raise ReadeckError("OAuth request timed out") from exc
        except httpx.RequestError as exc:
            raise ReadeckError("OAuth request failed") from exc
        if not response.is_success:
            raise self._oauth_error(response)
        try:
            return response.json()
        except ValueError as exc:
            raise ReadeckError("OAuth endpoint returned invalid JSON") from exc

    async def get_info(self) -> ReadeckInfo:
        """Get public instance information, including advertised features."""
        try:
            data = await self._request_json("GET", "api/info")
            return ReadeckInfo.model_validate(data)
        except ValidationError as exc:
            raise ReadeckError("Invalid instance information response") from exc

    async def get_server_metadata(self) -> OAuthServerMetadata:
        """Retrieve OAuth authorization-server metadata for this instance."""
        try:
            return OAuthServerMetadata.model_validate(
                await self._request_json(
                    "GET", ".well-known/oauth-authorization-server"
                )
            )
        except ValidationError as exc:
            raise ReadeckError("Invalid OAuth server metadata response") from exc

    async def register_client(
        self, registration: OAuthClientRegistrationRequest
    ) -> OAuthClientRegistration:
        """Register a public OAuth client using dynamic client registration."""
        try:
            data = await self._request_json(
                "POST",
                "api/oauth/client",
                json=registration.model_dump(mode="json", exclude_none=True),
            )
            return OAuthClientRegistration.model_validate(data)
        except ValidationError as exc:
            raise ReadeckError("Invalid client registration response") from exc

    async def start_device_authorization(
        self, client_id: str, scope: str
    ) -> DeviceAuthorization:
        """Initiate an OAuth device authorization flow."""
        try:
            data = await self._request_json(
                "POST",
                "api/oauth/device",
                data={"client_id": client_id, "scope": scope},
            )
            return DeviceAuthorization.model_validate(data)
        except ValidationError as exc:
            raise ReadeckError("Invalid device authorization response") from exc

    async def poll_device_token(
        self, authorization: DeviceAuthorization, client_id: str
    ) -> OAuthToken:
        """Poll until device authorization completes or the request expires.

        The server-provided interval is respected between pending responses and
        increased by five seconds when the standard ``slow_down`` error occurs.
        """
        interval = authorization.interval
        deadline = time.monotonic() + authorization.expires_in
        while True:
            try:
                data = await self._request_json(
                    "POST",
                    "api/oauth/token",
                    data={
                        "grant_type": DEVICE_CODE_GRANT,
                        "device_code": authorization.device_code,
                        "client_id": client_id,
                    },
                )
                return OAuthToken.model_validate(data)
            except ReadeckOAuthPendingError:
                pass
            except ReadeckOAuthSlowDownError:
                interval += 5
            except ValidationError as exc:
                raise ReadeckError("Invalid OAuth token response") from exc

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReadeckOAuthError("expired_token")
            await asyncio.sleep(min(interval, remaining))

    async def revoke_token(self, token: str) -> None:
        """Revoke a token. Readeck requires the same bearer token to authorize this."""
        try:
            response = await self._client.post(
                self._url("api/oauth/revoke"),
                data={"token": token},
                headers={"Authorization": f"Bearer {token}"},
            )
        except httpx.TimeoutException as exc:
            raise ReadeckError("OAuth request timed out") from exc
        except httpx.RequestError as exc:
            raise ReadeckError("OAuth request failed") from exc
        if not response.is_success:
            raise self._oauth_error(response)
