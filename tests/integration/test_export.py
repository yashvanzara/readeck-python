"""Live bookmark export tests."""

import pytest

from readeck import ReadeckClient

from .waiters import wait_until_loaded

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_export_markdown_and_epub(
    readeck_client: ReadeckClient, created_bookmarks: list[str]
) -> None:
    created = await readeck_client.create_bookmark(
        url="https://example.com",
        title="Export Target",
        labels=["export"],
    )
    assert created.bookmark_id
    created_bookmarks.append(created.bookmark_id)
    bookmark = await wait_until_loaded(readeck_client, created.bookmark_id)

    if not bookmark.loaded and not bookmark.has_article:
        pytest.skip("Readeck did not finish extracting the bookmark")

    markdown = await readeck_client.export_bookmark(created.bookmark_id, format="md")
    assert isinstance(markdown, str)
    assert markdown.strip()

    parsed = await readeck_client.export_bookmark_parsed(created.bookmark_id)
    assert parsed.raw_content.strip()
    assert parsed.content is not None

    epub = await readeck_client.export_bookmark(created.bookmark_id, format="epub")
    assert isinstance(epub, bytes)
    assert len(epub) > 0
