"""Live highlights listing."""

import pytest

from readeck import HighlightListResponse, ReadeckClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_highlights(readeck_client: ReadeckClient) -> None:
    result = await readeck_client.get_highlights(limit=10)
    assert isinstance(result, HighlightListResponse)
    assert result.total_count >= 0
    assert result.page >= 1
    assert isinstance(result.items, list)
