"""Polling helpers for asynchronous Readeck operations."""

from __future__ import annotations

import asyncio

from readeck import Bookmark, ReadeckClient, ReadeckError


async def wait_until_loaded(
    client: ReadeckClient,
    bookmark_id: str,
    timeout: float = 30.0,
) -> Bookmark:
    """Poll until a bookmark reports that content extraction finished."""
    deadline = asyncio.get_running_loop().time() + timeout
    last_error: Exception | None = None
    bookmark: Bookmark | None = None
    while asyncio.get_running_loop().time() < deadline:
        try:
            bookmark = await client.get_bookmark(bookmark_id)
            if bookmark.loaded or bookmark.has_article:
                return bookmark
        except ReadeckError as exc:
            last_error = exc
        await asyncio.sleep(1)
    if bookmark is not None:
        return bookmark
    raise AssertionError(
        f"Bookmark {bookmark_id} was not available before timeout: {last_error}"
    )
