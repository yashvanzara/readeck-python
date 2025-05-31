"""Pydantic models for Readeck API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

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
    permissions: List[str] = Field(
        ..., description="Permissions granted for this session"
    )
    roles: List[str] = Field(..., description="Roles granted for this session")


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
    height: Optional[int] = Field(default=0, description="Resource height")
    width: Optional[int] = Field(default=0, description="Resource width")


class BookmarkResources(BaseModel):
    """Collection of bookmark resources."""

    article: Optional[BookmarkResource] = Field(
        default=None, description="Article resource"
    )
    icon: Optional[BookmarkResource] = Field(default=None, description="Icon resource")
    image: Optional[BookmarkResource] = Field(
        default=None, description="Image resource"
    )
    log: Optional[BookmarkResource] = Field(default=None, description="Log resource")
    props: Optional[BookmarkResource] = Field(
        default=None, description="Properties resource"
    )
    thumbnail: Optional[BookmarkResource] = Field(
        default=None, description="Thumbnail resource"
    )


class Bookmark(BaseModel):
    """Bookmark information."""

    id: str = Field(..., description="Bookmark ID")
    href: str = Field(..., description="Original bookmark URL")
    url: str = Field(..., description="Canonical URL")
    title: str = Field(..., description="Bookmark title")
    description: Optional[str] = Field(default="", description="Bookmark description")
    site: Optional[str] = Field(default="", description="Site domain")
    site_name: Optional[str] = Field(default="", description="Site name")
    authors: List[str] = Field(default_factory=list, description="Article authors")
    type: str = Field(..., description="Bookmark type (article, photo, video)")
    document_type: Optional[str] = Field(default="", description="Document type")
    lang: Optional[str] = Field(default="", description="Content language")
    text_direction: Optional[str] = Field(
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
    labels: List[str] = Field(default_factory=list, description="Bookmark labels")

    # Timestamps
    created: datetime = Field(..., description="Creation timestamp")
    updated: datetime = Field(..., description="Last update timestamp")
    published: Optional[datetime] = Field(
        default=None, description="Publication timestamp"
    )

    # Resources
    resources: Optional[BookmarkResources] = Field(
        default=None, description="Associated resources"
    )

    # Additional fields for detailed bookmark response
    links: Optional[List[BookmarkLink]] = Field(
        default=None, description="Links found in the bookmark"
    )
    read_anchor: Optional[str] = Field(
        default=None, description="Reading anchor position"
    )

    @field_serializer("created", "updated", "published", when_used="json")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format."""
        if value is None:
            return None
        return value.isoformat()


class BookmarkListParams(BaseModel):
    """Parameters for fetching bookmark lists."""

    limit: Optional[int] = Field(default=None, description="Number of items per page")
    offset: Optional[int] = Field(default=None, description="Pagination offset")
    sort: Optional[List[str]] = Field(default=None, description="Sorting parameters")
    search: Optional[str] = Field(default=None, description="Full text search string")
    title: Optional[str] = Field(default=None, description="Filter by bookmark title")
    author: Optional[str] = Field(default=None, description="Filter by author name")
    site: Optional[str] = Field(
        default=None, description="Filter by site name or domain"
    )
    type: Optional[List[str]] = Field(
        default=None, description="Filter by bookmark type"
    )
    labels: Optional[str] = Field(default=None, description="Filter by labels")
    is_loaded: Optional[bool] = Field(
        default=None, description="Filter by loaded state"
    )
    has_errors: Optional[bool] = Field(
        default=None, description="Filter bookmarks with/without errors"
    )
    has_labels: Optional[bool] = Field(
        default=None, description="Filter bookmarks with/without labels"
    )
    is_marked: Optional[bool] = Field(
        default=None, description="Filter by marked (favorite) status"
    )
    is_archived: Optional[bool] = Field(
        default=None, description="Filter by archived status"
    )
    range_start: Optional[str] = Field(default=None, description="Date range start")
    range_end: Optional[str] = Field(default=None, description="Date range end")
    read_status: Optional[List[str]] = Field(
        default=None, description="Read progress status"
    )
    updated_since: Optional[datetime] = Field(
        default=None, description="Retrieve bookmarks updated after this date"
    )
    id: Optional[str] = Field(default=None, description="Filter by bookmark ID(s)")
    collection: Optional[str] = Field(
        default=None, description="Filter by collection ID"
    )

    @field_serializer("updated_since", when_used="json")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format."""
        if value is None:
            return None
        return value.isoformat()

    def to_query_params(self) -> Dict[str, Any]:
        """Convert parameters to query string dictionary."""
        params: Dict[str, Any] = {}

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
    title: Optional[str] = Field(
        default=None, description="Optional title for the bookmark"
    )
    labels: List[str] = Field(
        default_factory=list, description="Optional labels for the bookmark"
    )


class BookmarkCreateResponse(BaseModel):
    """Response from creating a new bookmark."""

    message: str = Field(..., description="Response message")
    status: int = Field(..., description="Response status code")


class BookmarkCreateResult(BaseModel):
    """Complete result from creating a bookmark, including response headers."""

    response: BookmarkCreateResponse = Field(..., description="API response body")
    bookmark_id: Optional[str] = Field(
        default=None, description="ID of the created bookmark from Bookmark-Id header"
    )
    location: Optional[str] = Field(
        default=None, description="URL of the created resource from Location header"
    )


class MarkdownExportMetadata(BaseModel):
    """Metadata parsed from markdown export YAML frontmatter."""

    title: Optional[str] = Field(default=None, description="Article title")
    saved: Optional[str] = Field(
        default=None, description="Date when bookmark was saved"
    )
    published: Optional[str] = Field(default=None, description="Publication date")
    website: Optional[str] = Field(default=None, description="Website domain")
    source: Optional[str] = Field(default=None, description="Source URL")
    authors: Optional[List[str]] = Field(default=None, description="Article authors")
    labels: Optional[List[str]] = Field(default=None, description="Bookmark labels")


class MarkdownExportResult(BaseModel):
    """Result of markdown export with parsed metadata and content."""

    metadata: Optional[MarkdownExportMetadata] = Field(
        default=None, description="Parsed frontmatter metadata"
    )
    content: str = Field(..., description="Markdown content without frontmatter")
    raw_content: str = Field(
        ..., description="Original markdown content including frontmatter"
    )
