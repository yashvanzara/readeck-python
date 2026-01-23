"""Pydantic models for Readeck API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer


class EmailSettings(BaseModel):
    """Email settings configuration."""

    reply_to: str = Field(default="", description="Reply-to email address")
    epub_to: str = Field(default="", description="EPUB destination email address")


class ReaderSettings(BaseModel):
    """Reader settings configuration."""

    font: str = Field(..., description="Font family for the reader")
    font_size: int = Field(..., description="Font size for the reader")
    line_height: int = Field(..., description="Line height for the reader")
    width: int = Field(default=0, description="Reader width setting")
    justify: int = Field(default=0, description="Text justification setting")
    hyphenation: int = Field(default=0, description="Hyphenation setting")


class UserSettings(BaseModel):
    """User settings and preferences."""

    debug_info: bool = Field(..., description="Enable debug information")
    reader_settings: ReaderSettings = Field(..., description="Reader configuration")
    lang: str = Field(default="en-US", description="Language setting")
    addon_reminder: bool = Field(default=True, description="Show addon reminders")
    email_settings: EmailSettings = Field(
        default_factory=EmailSettings, description="Email configuration"
    )


class User(BaseModel):
    """User information."""

    created: datetime = Field(..., description="Account creation date")
    email: str = Field(..., description="User email address")
    updated: datetime = Field(..., description="Last update date")
    username: str = Field(..., description="Username")
    settings: UserSettings = Field(..., description="User settings")

    @field_serializer("created", "updated", when_used="json")
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime fields to ISO format."""
        return value.isoformat()


class Provider(BaseModel):
    """Authentication provider information."""

    application: str = Field(default="", description="The registered application name")
    id: str = Field(default="", description="Authentication provider ID (token ID)")
    name: str = Field(..., description="Provider name")
    permissions: list[str] = Field(
        ..., description="Permissions granted for this session"
    )
    roles: list[str] = Field(..., description="Roles granted for this session")


class UserProfile(BaseModel):
    """Complete user profile response."""

    provider: Provider = Field(..., description="Authentication provider information")
    user: User = Field(..., description="User information and settings")

    @field_serializer("provider", "user", when_used="json")
    def serialize_nested_models(self, value: Any) -> Any:
        """Serialize nested models that may contain datetime fields."""
        if hasattr(value, "model_dump"):
            return value.model_dump()
        return value


class BookmarkLink(BaseModel):
    """Link reference in a bookmark."""

    content_type: str = Field(..., description="Content type of the link")
    domain: str = Field(..., description="Domain of the link")
    is_page: bool = Field(..., description="Whether this is a page link")
    title: str = Field(..., description="Title of the link")
    url: str = Field(..., description="URL of the link")


class BookmarkResource(BaseModel):
    """Resource reference for a bookmark."""

    src: str = Field(..., description="Resource URL")
    height: int | None = Field(default=0, description="Resource height")
    width: int | None = Field(default=0, description="Resource width")


class BookmarkResources(BaseModel):
    """Collection of bookmark resources."""

    article: BookmarkResource | None = Field(
        default=None, description="Article resource"
    )
    icon: BookmarkResource | None = Field(default=None, description="Icon resource")
    image: BookmarkResource | None = Field(default=None, description="Image resource")
    log: BookmarkResource | None = Field(default=None, description="Log resource")
    props: BookmarkResource | None = Field(
        default=None, description="Properties resource"
    )
    thumbnail: BookmarkResource | None = Field(
        default=None, description="Thumbnail resource"
    )


class Bookmark(BaseModel):
    """Bookmark information."""

    id: str = Field(..., description="Bookmark ID")
    href: str = Field(..., description="Original bookmark URL")
    url: str = Field(..., description="Canonical URL")
    title: str = Field(..., description="Bookmark title")
    description: str | None = Field(default="", description="Bookmark description")
    site: str | None = Field(default="", description="Site domain")
    site_name: str | None = Field(default="", description="Site name")
    authors: list[str] = Field(default_factory=list, description="Article authors")
    type: str = Field(..., description="Bookmark type (article, photo, video)")
    document_type: str | None = Field(default="", description="Document type")
    lang: str | None = Field(default="", description="Content language")
    text_direction: str | None = Field(
        default="ltr", description="Text direction (ltr, rtl)"
    )

    # State and flags
    loaded: bool = Field(default=False, description="Whether content is loaded")
    has_article: bool = Field(
        default=False, description="Whether article content is available"
    )
    is_archived: bool = Field(default=False, description="Whether bookmark is archived")
    is_deleted: bool = Field(default=False, description="Whether bookmark is deleted")
    is_marked: bool = Field(
        default=False, description="Whether bookmark is marked as favorite"
    )

    # Content metadata
    word_count: int = Field(default=0, description="Article word count")
    reading_time: int = Field(
        default=0, description="Estimated reading time in minutes"
    )
    read_progress: float = Field(
        default=0.0, description="Reading progress (0.0 to 1.0)"
    )
    state: int = Field(default=0, description="Bookmark state")

    # Labels and organization
    labels: list[str] = Field(default_factory=list, description="Bookmark labels")

    # Timestamps
    created: datetime = Field(..., description="Creation timestamp")
    updated: datetime = Field(..., description="Last update timestamp")
    published: datetime | None = Field(
        default=None, description="Publication timestamp"
    )

    # Resources
    resources: BookmarkResources | None = Field(
        default=None, description="Associated resources"
    )

    # Additional fields for detailed bookmark response
    links: list[BookmarkLink] | None = Field(
        default=None, description="Links found in the bookmark"
    )
    read_anchor: str | None = Field(default=None, description="Reading anchor position")

    @field_serializer("created", "updated", "published", when_used="json")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """Serialize datetime fields to ISO format."""
        if value is None:
            return None
        return value.isoformat()


class BookmarkListParams(BaseModel):
    """Parameters for fetching bookmark lists."""

    limit: int | None = Field(default=None, description="Number of items per page")
    offset: int | None = Field(default=None, description="Pagination offset")
    sort: list[str] | None = Field(default=None, description="Sorting parameters")
    search: str | None = Field(default=None, description="Full text search string")
    title: str | None = Field(default=None, description="Filter by bookmark title")
    author: str | None = Field(default=None, description="Filter by author name")
    site: str | None = Field(default=None, description="Filter by site name or domain")
    type: list[str] | None = Field(default=None, description="Filter by bookmark type")
    labels: str | None = Field(default=None, description="Filter by labels")
    is_loaded: bool | None = Field(default=None, description="Filter by loaded state")
    has_errors: bool | None = Field(
        default=None, description="Filter bookmarks with/without errors"
    )
    has_labels: bool | None = Field(
        default=None, description="Filter bookmarks with/without labels"
    )
    is_marked: bool | None = Field(
        default=None, description="Filter by marked (favorite) status"
    )
    is_archived: bool | None = Field(
        default=None, description="Filter by archived status"
    )
    range_start: str | None = Field(default=None, description="Date range start")
    range_end: str | None = Field(default=None, description="Date range end")
    read_status: list[str] | None = Field(
        default=None, description="Read progress status"
    )
    updated_since: datetime | None = Field(
        default=None, description="Retrieve bookmarks updated after this date"
    )
    id: str | None = Field(default=None, description="Filter by bookmark ID(s)")
    collection: str | None = Field(default=None, description="Filter by collection ID")

    @field_serializer("updated_since", when_used="json")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """Serialize datetime fields to ISO format."""
        if value is None:
            return None
        return value.isoformat()

    def to_query_params(self) -> dict[str, Any]:
        """Convert parameters to query string dictionary."""
        params: dict[str, Any] = {}

        for field_name, field_value in self.model_dump(exclude_none=True).items():
            if field_value is None:
                continue

            if isinstance(field_value, list):
                # For single item lists, convert to string
                # For multiple item lists, keep as list
                if len(field_value) == 1:
                    params[field_name] = field_value[0]
                else:
                    params[field_name] = field_value
            elif isinstance(field_value, datetime):
                # Convert datetime to ISO format
                params[field_name] = field_value.isoformat()
            else:
                params[field_name] = field_value

        return params


class BookmarkCreateRequest(BaseModel):
    """Request payload for creating a new bookmark."""

    url: str = Field(..., description="The URL to bookmark")
    title: str | None = Field(
        default=None, description="Optional title for the bookmark"
    )
    labels: list[str] = Field(
        default_factory=list, description="Optional labels for the bookmark"
    )


class BookmarkCreateResponse(BaseModel):
    """Response from creating a new bookmark."""

    message: str = Field(..., description="Response message")
    status: int = Field(..., description="Response status code")


class BookmarkCreateResult(BaseModel):
    """Complete result from creating a bookmark, including response headers."""

    response: BookmarkCreateResponse = Field(..., description="API response body")
    bookmark_id: str | None = Field(
        default=None, description="ID of the created bookmark from Bookmark-Id header"
    )
    location: str | None = Field(
        default=None, description="URL of the created resource from Location header"
    )


class MarkdownExportMetadata(BaseModel):
    """Metadata parsed from markdown export YAML frontmatter."""

    title: str | None = Field(default=None, description="Article title")
    saved: str | None = Field(default=None, description="Date when bookmark was saved")
    published: str | None = Field(default=None, description="Publication date")
    website: str | None = Field(default=None, description="Website domain")
    source: str | None = Field(default=None, description="Source URL")
    authors: list[str] | None = Field(default=None, description="Article authors")
    labels: list[str] | None = Field(default=None, description="Bookmark labels")


class Highlight(BaseModel):
    """A single highlight/annotation from a bookmark."""

    id: str = Field(..., description="Unique identifier for the highlight")
    href: str = Field(..., description="API URL for the highlight")
    bookmark_id: str = Field(..., description="ID of the bookmarked content")
    bookmark_href: str = Field(..., description="API URL of the bookmarked content")
    bookmark_title: str = Field(..., description="Title of the bookmarked content")
    bookmark_url: str = Field(..., description="URL of the bookmarked content")
    bookmark_site_name: str | None = Field(
        default=None, description="Name of the website where the content is from"
    )
    text: str = Field(..., description="The highlighted text content")
    created: datetime = Field(..., description="When the highlight was created")
    updated: datetime | None = Field(
        default=None, description="When the highlight was last updated"
    )

    @field_serializer("created", "updated", when_used="json")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """Serialize datetime fields to ISO format."""
        return value.isoformat() if value is not None else None


class HighlightListResponse(BaseModel):
    """Response model for the list highlights endpoint."""

    items: list[Highlight] = Field(
        default_factory=list, description="List of highlights"
    )
    total_count: int = Field(..., description="Total number of highlights available")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages available")
    links: dict[str, str | None] = Field(
        default_factory=dict, description="Pagination links"
    )


class HighlightListParams(BaseModel):
    """Parameters for fetching highlights list."""

    limit: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Number of items per page (1-100)",
    )
    offset: int | None = Field(default=None, ge=0, description="Pagination offset")

    def to_query_params(self) -> dict[str, str | int]:
        """Convert parameters to query string dictionary."""
        params: dict[str, str | int] = {}
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        return params


class MarkdownExportResult(BaseModel):
    """Result of markdown export with parsed metadata and content."""

    metadata: MarkdownExportMetadata | None = Field(
        default=None, description="Parsed frontmatter metadata"
    )
    content: str = Field(..., description="Markdown content without frontmatter")
    raw_content: str = Field(
        ..., description="Original markdown content including frontmatter"
    )
