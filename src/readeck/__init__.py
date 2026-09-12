"""Readeck Python Client Library.

A Python client library for the Readeck API, providing easy access to
Readeck's bookmark and reading features.
"""

__version__ = "0.2.1"
__author__ = "Yash Vanzara"
__email__ = "yashvanzara@gmail.com"

from .client import ReadeckClient
from .exceptions import (
    ReadeckAuthError,
    ReadeckError,
    ReadeckNotFoundError,
    ReadeckOAuthError,
    ReadeckOAuthPendingError,
    ReadeckOAuthSlowDownError,
    ReadeckServerError,
    ReadeckValidationError,
)
from .models import (
    Bookmark,
    BookmarkCreateRequest,
    BookmarkCreateResponse,
    BookmarkCreateResult,
    BookmarkLink,
    BookmarkListParams,
    BookmarkResource,
    BookmarkResources,
    BookmarkUpdateRequest,
    BookmarkUpdateResponse,
    DeviceAuthorization,
    EmailSettings,
    Highlight,
    HighlightListParams,
    HighlightListResponse,
    Label,
    MarkdownExportMetadata,
    MarkdownExportResult,
    OAuthClientRegistration,
    OAuthClientRegistrationRequest,
    OAuthServerMetadata,
    OAuthToken,
    Provider,
    ReadeckInfo,
    ReadeckVersion,
    ReaderSettings,
    User,
    UserProfile,
    UserSettings,
)
from .oauth import ReadeckOAuthClient

__all__ = [
    "ReadeckClient",
    "ReadeckOAuthClient",
    "ReadeckError",
    "ReadeckAuthError",
    "ReadeckNotFoundError",
    "ReadeckOAuthError",
    "ReadeckOAuthPendingError",
    "ReadeckOAuthSlowDownError",
    "ReadeckServerError",
    "ReadeckValidationError",
    "UserProfile",
    "User",
    "Provider",
    "UserSettings",
    "ReaderSettings",
    "EmailSettings",
    "Bookmark",
    "Highlight",
    "HighlightListParams",
    "HighlightListResponse",
    "BookmarkCreateRequest",
    "BookmarkCreateResponse",
    "BookmarkCreateResult",
    "BookmarkLink",
    "BookmarkListParams",
    "BookmarkUpdateRequest",
    "BookmarkUpdateResponse",
    "BookmarkResource",
    "BookmarkResources",
    "MarkdownExportMetadata",
    "MarkdownExportResult",
    "Label",
    "ReadeckInfo",
    "ReadeckVersion",
    "OAuthServerMetadata",
    "OAuthClientRegistrationRequest",
    "OAuthClientRegistration",
    "DeviceAuthorization",
    "OAuthToken",
]
