"""Helpers for Docker Compose integration tests."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

COMPOSE_FILE = Path(__file__).parent / "compose.yaml"
COMPOSE_PROJECT = "readeck-python-itest"
BASE_URL = "http://127.0.0.1:18765"
TEST_USERNAME = "itest"
TEST_PASSWORD = "ItestPass123!"
TEST_EMAIL = "itest@example.com"

BEARER_TOKEN = re.compile(r"Authorization:\s*Bearer\s+([A-Za-z0-9]+)")
CLIPBOARD_VALUE = re.compile(
    r'data-clipboard-target="content"\s+value="([^"]+)"',
    re.I,
)


@dataclass(frozen=True)
class ReadeckStack:
    """Running Readeck Compose stack."""

    base_url: str
    data_dir: Path


@dataclass(frozen=True)
class ReadeckCredentials:
    """API credentials for the integration-test user."""

    base_url: str
    token: str
    username: str
    password: str


def docker_available() -> bool:
    """Return True when the Docker daemon responds."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def compose_env(data_dir: Path) -> dict[str, str]:
    """Build an environment with the Compose data-directory override."""
    env = os.environ.copy()
    env["READECK_ITEST_DATA"] = str(data_dir)
    return env


def compose(
    args: list[str],
    data_dir: Path,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    """Run a docker compose command for the integration-test project."""
    return subprocess.run(
        [
            "docker",
            "compose",
            "-p",
            COMPOSE_PROJECT,
            "-f",
            str(COMPOSE_FILE),
            *args,
        ],
        env=compose_env(data_dir),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def compose_down(data_dir: Path) -> None:
    """Stop the stack and remove containers, networks, and volumes."""
    compose(
        ["down", "-v", "--remove-orphans", "--timeout", "10"],
        data_dir,
        timeout=60,
    )


def wait_for_http(base_url: str, timeout: float = 60.0) -> None:
    """Wait until the Readeck HTTP server accepts connections."""
    deadline = time.monotonic() + timeout
    last_error = "timeout"
    while time.monotonic() < deadline:
        try:
            response = httpx.get(base_url, follow_redirects=True, timeout=2.0)
            if response.status_code < 500:
                return
            last_error = f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f"Readeck did not become reachable at {base_url}: {last_error}")


def create_test_user(data_dir: Path) -> None:
    """Create or update the integration-test user via the Readeck CLI."""
    last = None
    for _ in range(10):
        last = compose(
            [
                "exec",
                "-T",
                "app",
                "/bin/readeck",
                "user",
                "-config",
                "config.toml",
                "-u",
                TEST_USERNAME,
                "-p",
                TEST_PASSWORD,
                "-email",
                TEST_EMAIL,
                "-group",
                "admin",
            ],
            data_dir,
            timeout=30,
        )
        if last.returncode == 0:
            return
        time.sleep(2)
    detail = ""
    if last is not None:
        detail = f"\nstdout:\n{last.stdout}\nstderr:\n{last.stderr}"
    raise RuntimeError(f"Failed to create Readeck test user.{detail}")


def _extract_api_token(html: str) -> str | None:
    match = BEARER_TOKEN.search(html)
    if match:
        return match.group(1)
    for match in CLIPBOARD_VALUE.finditer(html):
        value = match.group(1).strip()
        if value.startswith("Authorization:"):
            bearer = BEARER_TOKEN.search(value)
            if bearer:
                return bearer.group(1)
            continue
        if value:
            return value
    return None


def create_api_token(base_url: str, username: str, password: str) -> str:
    """Log in via the HTML form and create a Bearer token for API tests.

    Readeck's OpenAPI docs (``/docs/api``) describe script auth as: generate a
    token from ``/profile/tokens`` and send it as ``Authorization: Bearer``.
    There is no JSON login route that returns a token.
    """
    with httpx.Client(base_url=base_url, follow_redirects=True, timeout=30.0) as client:
        login = client.post(
            "/login",
            data={"username": username, "password": password, "r": ""},
        )
        if login.status_code >= 400:
            raise RuntimeError(
                f"Readeck login failed: HTTP {login.status_code}: {login.text[:300]}"
            )

        profile = client.get("/api/profile", headers={"Accept": "application/json"})
        if profile.status_code != 200:
            raise RuntimeError(
                "Readeck login did not establish a session: "
                f"HTTP {profile.status_code}: {profile.text[:300]}"
            )

        created = client.post("/profile/tokens")
        if created.status_code >= 400:
            raise RuntimeError(
                "Readeck token creation failed: "
                f"HTTP {created.status_code}: {created.text[:300]}"
            )
        token = _extract_api_token(created.text)
        if not token:
            raise RuntimeError("Readeck token page did not include an API token")
        return token


def remove_data_dir(data_dir: Path) -> None:
    """Delete the temporary Compose data directory."""
    shutil.rmtree(data_dir, ignore_errors=True)
