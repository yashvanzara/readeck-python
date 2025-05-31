"""Readeck Python Client Library.

A Python client library for the Readeck API, providing easy access to
Readeck's bookmark and reading features.
"""

__version__ = "0.1.4"
__author__ = "Yash Vanzara"
__email__ = "yashvanzara@gmail.com"

from .client import ReadeckClient
from .exceptions import (
    ReadeckAuthError,
    ReadeckError,
    ReadeckNotFoundError,
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
    EmailSettings,
    MarkdownExportMetadata,
    MarkdownExportResult,
    Provider,
    ReaderSettings,
    User,
    UserProfile,
    UserSettings,
)

__all__ = [
    "ReadeckClient",
    "ReadeckError",
    "ReadeckAuthError",
    "ReadeckNotFoundError",
    "ReadeckServerError",
    "ReadeckValidationError",
    "UserProfile",
    "User",
    "Provider",
    "UserSettings",
    "ReaderSettings",
    "EmailSettings",
    "Bookmark",
    "BookmarkCreateRequest",
    "BookmarkCreateResponse",
    "BookmarkCreateResult",
    "BookmarkLink",
    "BookmarkListParams",
    "BookmarkResource",
    "BookmarkResources",
    "MarkdownExportMetadata",
    "MarkdownExportResult",
]
