"""Tests for Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from readeck.models import Provider, ReaderSettings, User, UserProfile, UserSettings


class TestReaderSettings:
    """Test ReaderSettings model."""

    def test_valid_reader_settings(self):
        """Test creating valid reader settings."""
        settings = ReaderSettings(font="Arial", font_size=16, line_height=24)

        assert settings.font == "Arial"
        assert settings.font_size == 16
        assert settings.line_height == 24

    def test_reader_settings_validation(self):
        """Test reader settings validation."""
        with pytest.raises(ValidationError):
            ReaderSettings(font="Arial")  # Missing required fields


class TestUserSettings:
    """Test UserSettings model."""

    def test_valid_user_settings(self):
        """Test creating valid user settings."""
        reader_settings = ReaderSettings(font="Arial", font_size=16, line_height=24)

        settings = UserSettings(debug_info=True, reader_settings=reader_settings)

        assert settings.debug_info is True
        assert settings.reader_settings.font == "Arial"

    def test_nested_reader_settings(self):
        """Test nested reader settings creation."""
        settings = UserSettings(
            debug_info=False,
            reader_settings={"font": "Helvetica", "font_size": 14, "line_height": 20},
        )

        assert settings.reader_settings.font == "Helvetica"
        assert settings.reader_settings.font_size == 14


class TestUser:
    """Test User model."""

    def test_valid_user(self):
        """Test creating a valid user."""
        user_settings = UserSettings(
            debug_info=False,
            reader_settings=ReaderSettings(font="Arial", font_size=16, line_height=24),
        )

        user = User(
            created=datetime(2024, 1, 1, 10, 0, 0),
            email="test@example.com",
            updated=datetime(2024, 12, 1, 15, 30, 0),
            username="testuser",
            settings=user_settings,
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.settings.debug_info is False

    def test_user_datetime_parsing(self):
        """Test datetime parsing from ISO strings."""
        user = User(
            created="2024-01-01T10:00:00Z",
            email="test@example.com",
            updated="2024-12-01T15:30:00Z",
            username="testuser",
            settings={
                "debug_info": False,
                "reader_settings": {
                    "font": "Arial",
                    "font_size": 16,
                    "line_height": 24,
                },
            },
        )

        assert isinstance(user.created, datetime)
        assert isinstance(user.updated, datetime)


class TestProvider:
    """Test Provider model."""

    def test_valid_provider(self):
        """Test creating a valid provider."""
        provider = Provider(
            application="readeck",
            id="tok_12345",
            name="Local Provider",
            permissions=["read", "write"],
            roles=["user"],
        )

        assert provider.application == "readeck"
        assert provider.id == "tok_12345"
        assert provider.name == "Local Provider"
        assert "read" in provider.permissions
        assert "user" in provider.roles

    def test_empty_permissions_and_roles(self):
        """Test provider with empty permissions and roles."""
        provider = Provider(
            application="readeck",
            id="tok_12345",
            name="Limited Provider",
            permissions=[],
            roles=[],
        )

        assert provider.permissions == []
        assert provider.roles == []


class TestUserProfile:
    """Test UserProfile model."""

    def test_valid_user_profile(self, mock_user_profile_data):
        """Test creating a valid user profile."""
        profile = UserProfile.model_validate(mock_user_profile_data)

        assert profile.provider.application == "readeck"
        assert profile.user.username == "testuser"
        assert profile.user.email == "test@example.com"
        assert profile.user.settings.debug_info is False
        assert profile.user.settings.reader_settings.font == "Arial"

    def test_user_profile_json_serialization(self, mock_user_profile_data):
        """Test JSON serialization of user profile."""
        profile = UserProfile.model_validate(mock_user_profile_data)

        # Test that we can serialize and deserialize
        json_data = profile.model_dump()
        restored_profile = UserProfile.model_validate(json_data)

        assert restored_profile.user.username == profile.user.username
        assert restored_profile.provider.id == profile.provider.id

    def test_user_profile_validation_error(self):
        """Test validation error for invalid user profile data."""
        invalid_data = {
            "provider": {
                "application": "readeck",
                # Missing required fields
            },
            "user": {
                "username": "test"
                # Missing required fields
            },
        }

        with pytest.raises(ValidationError):
            UserProfile.model_validate(invalid_data)
