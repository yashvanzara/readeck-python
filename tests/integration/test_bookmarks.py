"""Live bookmark create, list, update, label, and delete tests."""

import pytest

from readeck import BookmarkListParams, BookmarkUpdateRequest, ReadeckClient
from readeck.exceptions import ReadeckNotFoundError

from .waiters import wait_until_loaded

pytestmark = pytest.mark.integration

EXAMPLE_URL = "https://example.com"
EXAMPLE_ORG_URL = "https://example.org"


@pytest.mark.asyncio
async def test_create_get_list_and_delete_bookmark(
    readeck_client: ReadeckClient, created_bookmarks: list[str]
) -> None:
    created = await readeck_client.create_bookmark(
        url=EXAMPLE_URL,
        title="Example Article",
        labels=["itest", "docs"],
    )
    assert created.bookmark_id
    created_bookmarks.append(created.bookmark_id)

    bookmark = await wait_until_loaded(readeck_client, created.bookmark_id)
    assert bookmark.id == created.bookmark_id
    assert EXAMPLE_URL in bookmark.url or bookmark.href.endswith("example.com/")
    assert "itest" in bookmark.labels

    listed = await readeck_client.get_bookmarks(BookmarkListParams(limit=50))
    assert any(item.id == created.bookmark_id for item in listed)

    searched = await readeck_client.get_bookmarks(
        BookmarkListParams(search="example", limit=50)
    )
    assert any(item.id == created.bookmark_id for item in searched)

    labeled = await readeck_client.get_bookmarks(
        BookmarkListParams(labels="itest", limit=50)
    )
    assert any(item.id == created.bookmark_id for item in labeled)

    await readeck_client.delete_bookmark(created.bookmark_id)
    created_bookmarks.remove(created.bookmark_id)
    with pytest.raises(ReadeckNotFoundError):
        await readeck_client.get_bookmark(created.bookmark_id)


@pytest.mark.asyncio
async def test_update_bookmark_and_labels(
    readeck_client: ReadeckClient, created_bookmarks: list[str]
) -> None:
    created = await readeck_client.create_bookmark(
        url=EXAMPLE_ORG_URL,
        title="Original Title",
        labels=["keep"],
    )
    assert created.bookmark_id
    created_bookmarks.append(created.bookmark_id)
    await wait_until_loaded(readeck_client, created.bookmark_id)

    updated = await readeck_client.update_bookmark(
        created.bookmark_id,
        BookmarkUpdateRequest(
            title="Updated Title",
            is_marked=True,
            add_labels=["added"],
        ),
    )
    assert created.bookmark_id in updated.href

    bookmark = await readeck_client.get_bookmark(created.bookmark_id)
    assert bookmark.title == "Updated Title"
    assert bookmark.is_marked is True
    assert "keep" in bookmark.labels
    assert "added" in bookmark.labels

    await readeck_client.update_bookmark(
        created.bookmark_id,
        BookmarkUpdateRequest(remove_labels=["added"]),
    )
    bookmark = await readeck_client.get_bookmark(created.bookmark_id)
    assert "added" not in bookmark.labels
    assert "keep" in bookmark.labels

    labels = await readeck_client.get_labels()
    names = {label.name for label in labels}
    assert "keep" in names
