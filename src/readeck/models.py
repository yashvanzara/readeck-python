"""Pydantic models for Readeck API responses."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


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

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
