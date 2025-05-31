"""Tests for markdown export parsing functionality."""

import pytest
from pytest_httpx import HTTPXMock

from readeck import MarkdownExportResult, ReadeckClient
from readeck.exceptions import ReadeckError


class TestMarkdownParsing:
    """Test markdown frontmatter parsing functionality."""

    def test_parse_markdown_frontmatter_with_metadata(self):
        """Test parsing markdown with YAML frontmatter."""
        markdown_content = """---
title: Modernizing Home Feed Pre-Ranking Stage
saved: "2025-05-29"
published: "2025-05-29"
website: medium.com
source: https://medium.com/pinterest-engineering/modernizing-home-feed-pre-ranking-stage-e636c9cdc36b?source=rss-ef81ef829bcb------2
authors:
    - Pinterest Engineering
labels:
    - RSS
---

# Article Content

This is the main article content after the frontmatter.

## Section 1

Some content here.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is not None
        assert metadata.title == "Modernizing Home Feed Pre-Ranking Stage"
        assert metadata.saved == "2025-05-29"
        assert metadata.published == "2025-05-29"
        assert metadata.website == "medium.com"
        assert (
            metadata.source
            == "https://medium.com/pinterest-engineering/modernizing-home-feed-pre-ranking-stage-e636c9cdc36b?source=rss-ef81ef829bcb------2"
        )
        assert metadata.authors == ["Pinterest Engineering"]
        assert metadata.labels == ["RSS"]

        assert content.startswith("# Article Content")
        assert "This is the main article content" in content
        assert "---" not in content  # Frontmatter should be removed

    def test_parse_markdown_frontmatter_without_metadata(self):
        """Test parsing markdown without YAML frontmatter."""
        markdown_content = """# Regular Article

This is a regular markdown article without frontmatter.

## Section 1

Some content here.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is None
        assert content == markdown_content  # Content unchanged

    def test_parse_markdown_frontmatter_incomplete(self):
        """Test parsing markdown with incomplete frontmatter (no closing ---)."""
        markdown_content = """---
title: Incomplete Frontmatter
author: Test Author

# Article Content

This has incomplete frontmatter.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is None
        assert content == markdown_content  # Content unchanged

    def test_parse_markdown_frontmatter_invalid_yaml(self):
        """Test parsing markdown with invalid YAML in frontmatter."""
        markdown_content = """---
title: Valid Title
invalid_yaml: [unclosed list
---

# Article Content

This has invalid YAML in frontmatter.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is None
        assert content == markdown_content  # Content unchanged

    def test_parse_markdown_frontmatter_empty(self):
        """Test parsing markdown with empty frontmatter."""
        markdown_content = """---
---

# Article Content

This has empty frontmatter.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is not None
        assert metadata.title is None
        assert metadata.authors is None
        assert metadata.labels is None

        assert content.startswith("# Article Content")

    def test_parse_markdown_frontmatter_partial_metadata(self):
        """Test parsing markdown with partial metadata."""
        markdown_content = """---
title: Partial Metadata Article
website: example.com
---

# Article Content

This has only some metadata fields.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is not None
        assert metadata.title == "Partial Metadata Article"
        assert metadata.website == "example.com"
        assert metadata.saved is None
        assert metadata.published is None
        assert metadata.authors is None
        assert metadata.labels is None

    def test_parse_markdown_frontmatter_multiple_authors_labels(self):
        """Test parsing markdown with multiple authors and labels."""
        markdown_content = """---
title: Multi-Author Article
authors:
    - John Doe
    - Jane Smith
    - Bob Johnson
labels:
    - technology
    - programming
    - python
    - web-development
---

# Multi-Author Article

Content from multiple authors.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is not None
        assert metadata.title == "Multi-Author Article"
        assert metadata.authors == ["John Doe", "Jane Smith", "Bob Johnson"]
        assert metadata.labels == [
            "technology",
            "programming",
            "python",
            "web-development",
        ]

    @pytest.mark.asyncio
    async def test_export_bookmark_parsed_success(self, httpx_mock: HTTPXMock):
        """Test successful parsed markdown export."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"
        markdown_content = """---
title: Test Article
saved: "2025-05-29"
published: "2025-05-28"
website: example.com
source: https://example.com/article
authors:
    - Test Author
labels:
    - test
    - example
---

# Test Article

This is a test article with frontmatter.

## Introduction

Some content here.
"""

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text=markdown_content,
            status_code=200,
            headers={"Content-Type": "text/markdown; charset=utf-8"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark_parsed(bookmark_id)

        assert isinstance(result, MarkdownExportResult)
        assert result.raw_content == markdown_content

        # Check metadata
        assert result.metadata is not None
        assert result.metadata.title == "Test Article"
        assert result.metadata.saved == "2025-05-29"
        assert result.metadata.published == "2025-05-28"
        assert result.metadata.website == "example.com"
        assert result.metadata.source == "https://example.com/article"
        assert result.metadata.authors == ["Test Author"]
        assert result.metadata.labels == ["test", "example"]

        # Check content without frontmatter
        assert result.content.startswith("# Test Article")
        assert "This is a test article with frontmatter" in result.content
        assert "---" not in result.content

    @pytest.mark.asyncio
    async def test_export_bookmark_parsed_no_frontmatter(self, httpx_mock: HTTPXMock):
        """Test parsed export with markdown that has no frontmatter."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"
        markdown_content = """# Regular Article

This is a regular article without frontmatter.

## Section 1

Some content here.
"""

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text=markdown_content,
            status_code=200,
            headers={"Content-Type": "text/markdown; charset=utf-8"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark_parsed(bookmark_id)

        assert isinstance(result, MarkdownExportResult)
        assert result.raw_content == markdown_content
        assert result.metadata is None
        assert result.content == markdown_content  # Content unchanged

    @pytest.mark.asyncio
    async def test_export_bookmark_parsed_error_propagation(
        self, httpx_mock: HTTPXMock
    ):
        """Test that errors from export_bookmark are properly propagated."""
        bookmark_id = "nonexistent"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            status_code=404,
            text="Not found",
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        with pytest.raises(ReadeckError):
            await client.export_bookmark_parsed(bookmark_id)

    @pytest.mark.asyncio
    async def test_export_bookmark_parsed_empty_content(self, httpx_mock: HTTPXMock):
        """Test parsed export with empty content."""
        bookmark_id = "SRvBnHrQhKpk96x2EyJjps"

        httpx_mock.add_response(
            method="GET",
            url=f"https://test.readeck.com/api/bookmarks/{bookmark_id}/article.md",  # noqa: E231
            text="",
            status_code=200,
            headers={"Content-Type": "text/markdown; charset=utf-8"},
        )

        client = ReadeckClient(base_url="https://test.readeck.com", token="test_token")

        result = await client.export_bookmark_parsed(bookmark_id)

        assert isinstance(result, MarkdownExportResult)
        assert result.raw_content == ""
        assert result.metadata is None
        assert result.content == ""

    def test_parse_markdown_frontmatter_whitespace_handling(self):
        """Test frontmatter parsing handles whitespace correctly."""
        markdown_content = """---
title: Whitespace Test
website: example.com
---


# Article with Extra Newlines

Content after multiple newlines.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is not None
        assert metadata.title == "Whitespace Test"
        assert metadata.website == "example.com"

        # Content should start without leading newlines
        assert content.startswith("# Article with Extra Newlines")

    def test_parse_markdown_frontmatter_special_characters(self):
        """Test frontmatter parsing with special characters in values."""
        markdown_content = """---
title: "Article with: Special Characters & Symbols"
source: "https://example.com/path?param=value&other=true"
authors:
    - "Author with Émojis 🚀"
    - "Another Author (PhD)"
---

# Article Content

Content here.
"""

        metadata, content = ReadeckClient._parse_markdown_frontmatter(markdown_content)

        assert metadata is not None
        assert metadata.title == "Article with: Special Characters & Symbols"
        assert metadata.source == "https://example.com/path?param=value&other=true"
        assert metadata.authors == ["Author with Émojis 🚀", "Another Author (PhD)"]
