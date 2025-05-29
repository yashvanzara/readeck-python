"""Readeck Python Client Library.

A Python client library for the Readeck API, providing easy access to
Readeck's bookmark and reading features.
"""

__version__ = "0.1.0"
__author__ = "Yash Vanzara"
__email__ = "yash@yashvanzara.com"

from .client import ReadeckClient
from .exceptions import ReadeckAuthError, ReadeckError, ReadeckNotFoundError
from .models import (
    EmailSettings,
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
    "UserProfile",
    "User",
    "Provider",
    "UserSettings",
    "ReaderSettings",
    "EmailSettings",
]
