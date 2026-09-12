"""Session fixtures for Dockerized Readeck integration tests."""

from __future__ import annotations

import atexit
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest

from readeck import ReadeckClient, ReadeckError, ReadeckOAuthClient

from .helpers import (
    BASE_URL,
    COMPOSE_FILE,
    TEST_PASSWORD,
    TEST_USERNAME,
    ReadeckCredentials,
    ReadeckStack,
    compose,
    compose_down,
    create_api_token,
    create_test_user,
    docker_available,
    remove_data_dir,
    wait_for_http,
)

_ACTIVE_DATA_DIR: Path | None = None


def _atexit_teardown() -> None:
    if _ACTIVE_DATA_DIR is None:
        return
    compose_down(_ACTIVE_DATA_DIR)
    remove_data_dir(_ACTIVE_DATA_DIR)


atexit.register(_atexit_teardown)


@pytest.fixture(scope="session")
def readeck_stack() -> Generator[ReadeckStack, None, None]:
    """Start Readeck, always tearing down leftover or current Compose state."""
    global _ACTIVE_DATA_DIR

    if not docker_available():
        pytest.skip("Docker daemon is not available")
    if not COMPOSE_FILE.exists():
        pytest.fail(f"Compose file is missing: {COMPOSE_FILE}")

    data_dir = Path(tempfile.mkdtemp(prefix="readeck-python-itest-"))
    data_dir.mkdir(parents=True, exist_ok=True)
    _ACTIVE_DATA_DIR = data_dir

    compose_down(data_dir)
    try:
        started = compose(
            ["up", "-d", "--wait", "--wait-timeout", "120"],
            data_dir,
            timeout=240,
        )
        if started.returncode != 0:
            logs = compose(["logs"], data_dir, timeout=30)
            pytest.fail(
                "Failed to start Readeck Compose stack.\n"
                f"stdout:\n{started.stdout}\nstderr:\n{started.stderr}\n"
                f"logs:\n{logs.stdout}\n{logs.stderr}"
            )
        wait_for_http(BASE_URL)
        yield ReadeckStack(base_url=BASE_URL, data_dir=data_dir)
    finally:
        compose_down(data_dir)
        remove_data_dir(data_dir)
        _ACTIVE_DATA_DIR = None


@pytest.fixture(scope="session")
def readeck_credentials(readeck_stack: ReadeckStack) -> ReadeckCredentials:
    """Create the test user and an API token against the live instance."""
    create_test_user(readeck_stack.data_dir)
    token = create_api_token(readeck_stack.base_url, TEST_USERNAME, TEST_PASSWORD)
    return ReadeckCredentials(
        base_url=readeck_stack.base_url,
        token=token,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
    )


@pytest.fixture
async def readeck_client(
    readeck_credentials: ReadeckCredentials,
) -> AsyncGenerator[ReadeckClient, None]:
    """Authenticated client closed after each test."""
    async with ReadeckClient(
        base_url=readeck_credentials.base_url,
        token=readeck_credentials.token,
    ) as client:
        yield client


@pytest.fixture
async def readeck_oauth_client(
    readeck_stack: ReadeckStack,
) -> AsyncGenerator[ReadeckOAuthClient, None]:
    """Unauthenticated OAuth client closed after each test."""
    async with ReadeckOAuthClient(base_url=readeck_stack.base_url) as client:
        yield client


@pytest.fixture
async def created_bookmarks(
    readeck_client: ReadeckClient,
) -> AsyncGenerator[list[str], None]:
    """Track bookmark IDs created during a test and delete them afterwards."""
    bookmark_ids: list[str] = []
    yield bookmark_ids
    for bookmark_id in bookmark_ids:
        try:
            await readeck_client.delete_bookmark(bookmark_id)
        except ReadeckError:
            pass
