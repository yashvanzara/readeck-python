"""Pydantic models for Readeck API responses."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ReaderSettings(BaseModel):
    """Reader settings configuration."""

    font: str = Field(..., description="Font family for the reader")
    font_size: int = Field(..., description="Font size for the reader")
    line_height: int = Field(..., description="Line height for the reader")


class UserSettings(BaseModel):
    """User settings and preferences."""

    debug_info: bool = Field(..., description="Enable debug information")
    reader_settings: ReaderSettings = Field(..., description="Reader configuration")


class User(BaseModel):
    """User information."""

    created: datetime = Field(..., description="Account creation date")
    email: str = Field(..., description="User email address")
    updated: datetime = Field(..., description="Last update date")
    username: str = Field(..., description="Username")
    settings: UserSettings = Field(..., description="User settings")


class Provider(BaseModel):
    """Authentication provider information."""

    application: str = Field(..., description="The registered application name")
    id: str = Field(..., description="Authentication provider ID (token ID)")
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
