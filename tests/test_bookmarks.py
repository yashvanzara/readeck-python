"""Tests for bookmark models."""

from datetime import datetime

from readeck.models import (
    Bookmark,
    BookmarkListParams,
    BookmarkResource,
    BookmarkResources,
)


class TestBookmarkResource:
    """Test BookmarkResource model."""

    def test_bookmark_resource_creation(self):
        """Test creating a bookmark resource."""
        resource = BookmarkResource(
            src="https://example.com/image.jpg", height=600, width=800
        )

        assert resource.src == "https://example.com/image.jpg"
        assert resource.height == 600
        assert resource.width == 800

    def test_bookmark_resource_optional_dimensions(self):
        """Test bookmark resource with optional dimensions."""
        resource = BookmarkResource(src="https://example.com/favicon.ico")

        assert resource.src == "https://example.com/favicon.ico"
        assert resource.height == 0
        assert resource.width == 0


class TestBookmarkResources:
    """Test BookmarkResources model."""

    def test_bookmark_resources_creation(self):
        """Test creating bookmark resources collection."""
        resources = BookmarkResources(
            article=BookmarkResource(src="https://example.com/article"),
            icon=BookmarkResource(
                src="https://example.com/icon.ico", height=32, width=32
            ),
            image=BookmarkResource(
                src="https://example.com/image.jpg", height=600, width=800
            ),
        )

        assert resources.article.src == "https://example.com/article"
        assert resources.icon.height == 32
        assert resources.image.width == 800

    def test_bookmark_resources_all_optional(self):
        """Test that all resources are optional."""
        resources = BookmarkResources()

        assert resources.article is None
        assert resources.icon is None
        assert resources.image is None
        assert resources.log is None
        assert resources.props is None
        assert resources.thumbnail is None


class TestBookmark:
    """Test Bookmark model."""

    def test_bookmark_creation_minimal(self):
        """Test creating a bookmark with minimal required fields."""
        bookmark = Bookmark(
            id="123",
            href="https://example.com",
            url="https://example.com",
            title="Example",
            type="article",
            created=datetime(2024, 1, 1, 12, 0, 0),
            updated=datetime(2024, 1, 1, 12, 0, 0),
        )

        assert bookmark.id == "123"
        assert bookmark.href == "https://example.com"
        assert bookmark.url == "https://example.com"
        assert bookmark.title == "Example"
        assert bookmark.type == "article"
        assert bookmark.description == ""
        assert bookmark.authors == []
        assert bookmark.labels == []
        assert bookmark.loaded is False
        assert bookmark.is_marked is False

    def test_bookmark_creation_full(self, mock_bookmark_data):
        """Test creating a bookmark with full data."""
        bookmark = Bookmark.model_validate(mock_bookmark_data)

        assert bookmark.id == "abc123"
        assert bookmark.title == "Example Article"
        assert bookmark.authors == ["John Doe"]
        assert bookmark.labels == ["programming", "tutorial"]
        assert bookmark.word_count == 1500
        assert bookmark.reading_time == 6
        assert bookmark.resources is not None
        assert bookmark.resources.article.src == "https://example.com/article/content"
        assert bookmark.resources.icon.height == 32

    def test_bookmark_datetime_handling(self):
        """Test bookmark datetime field handling."""
        created_time = datetime(2024, 1, 15, 10, 30, 0)
        updated_time = datetime(2024, 1, 15, 11, 0, 0)
        published_time = datetime(2024, 1, 15, 8, 0, 0)

        bookmark = Bookmark(
            id="123",
            href="https://example.com",
            url="https://example.com",
            title="Test",
            type="article",
            created=created_time,
            updated=updated_time,
            published=published_time,
        )

        assert bookmark.created == created_time
        assert bookmark.updated == updated_time
        assert bookmark.published == published_time

    def test_bookmark_optional_published(self):
        """Test bookmark with optional published date."""
        bookmark = Bookmark(
            id="123",
            href="https://example.com",
            url="https://example.com",
            title="Test",
            type="article",
            created=datetime(2024, 1, 1, 12, 0, 0),
            updated=datetime(2024, 1, 1, 12, 0, 0),
        )

        assert bookmark.published is None


class TestBookmarkListParams:
    """Test BookmarkListParams model."""

    def test_bookmark_list_params_empty(self):
        """Test creating empty bookmark list parameters."""
        params = BookmarkListParams()
        query_params = params.to_query_params()

        assert query_params == {}

    def test_bookmark_list_params_basic(self):
        """Test basic bookmark list parameters."""
        params = BookmarkListParams(limit=10, offset=20, search="python")
        query_params = params.to_query_params()

        assert query_params["limit"] == 10
        assert query_params["offset"] == 20
        assert query_params["search"] == "python"

    def test_bookmark_list_params_boolean(self):
        """Test boolean parameters."""
        params = BookmarkListParams(is_marked=True, is_archived=False, has_labels=True)
        query_params = params.to_query_params()

        assert query_params["is_marked"] is True
        assert query_params["is_archived"] is False
        assert query_params["has_labels"] is True

    def test_bookmark_list_params_list_single(self):
        """Test list parameters with single item."""
        params = BookmarkListParams(type=["article"], sort=["created"])
        query_params = params.to_query_params()

        assert query_params["type"] == "article"
        assert query_params["sort"] == "created"

    def test_bookmark_list_params_list_multiple(self):
        """Test list parameters with multiple items."""
        params = BookmarkListParams(
            type=["article", "video"],
            sort=["created", "-title"],
            read_status=["unread", "reading"],
        )
        query_params = params.to_query_params()

        # Multiple values should be handled as lists
        assert query_params["type"] == ["article", "video"]
        assert query_params["sort"] == ["created", "-title"]
        assert query_params["read_status"] == ["unread", "reading"]

    def test_bookmark_list_params_datetime(self):
        """Test datetime parameter conversion."""
        updated_since = datetime(2024, 1, 1, 12, 0, 0)
        params = BookmarkListParams(updated_since=updated_since)
        query_params = params.to_query_params()

        assert query_params["updated_since"] == "2024-01-01T12:00:00"

    def test_bookmark_list_params_all_fields(self):
        """Test all bookmark list parameters."""
        updated_since = datetime(2024, 1, 1, 12, 0, 0)
        params = BookmarkListParams(
            limit=50,
            offset=100,
            sort=["created", "-title"],
            search="programming",
            title="Python",
            author="John Doe",
            site="example.com",
            type=["article", "video"],
            labels="python,tutorial",
            is_loaded=True,
            has_errors=False,
            has_labels=True,
            is_marked=True,
            is_archived=False,
            range_start="2024-01-01",
            range_end="2024-12-31",
            read_status=["unread", "reading"],
            updated_since=updated_since,
            id="bookmark123",
            collection="collection456",
        )

        query_params = params.to_query_params()

        assert query_params["limit"] == 50
        assert query_params["offset"] == 100
        assert query_params["sort"] == ["created", "-title"]
        assert query_params["search"] == "programming"
        assert query_params["title"] == "Python"
        assert query_params["author"] == "John Doe"
        assert query_params["site"] == "example.com"
        assert query_params["type"] == ["article", "video"]
        assert query_params["labels"] == "python,tutorial"
        assert query_params["is_loaded"] is True
        assert query_params["has_errors"] is False
        assert query_params["has_labels"] is True
        assert query_params["is_marked"] is True
        assert query_params["is_archived"] is False
        assert query_params["range_start"] == "2024-01-01"
        assert query_params["range_end"] == "2024-12-31"
        assert query_params["read_status"] == ["unread", "reading"]
        assert query_params["updated_since"] == "2024-01-01T12:00:00"
        assert query_params["id"] == "bookmark123"
        assert query_params["collection"] == "collection456"

    def test_bookmark_list_params_none_values_excluded(self):
        """Test that None values are excluded from query params."""
        params = BookmarkListParams(
            limit=10, offset=None, search="test"  # This should be excluded
        )
        query_params = params.to_query_params()

        assert "offset" not in query_params
        assert query_params["limit"] == 10
        assert query_params["search"] == "test"
