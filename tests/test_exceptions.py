"""Tests for custom exceptions."""

from readeck.exceptions import (
    ReadeckAuthError,
    ReadeckError,
    ReadeckNotFoundError,
    ReadeckServerError,
    ReadeckValidationError,
)


class TestReadeckError:
    """Test base ReadeckError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = ReadeckError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response_data is None

    def test_error_with_status_code(self):
        """Test error with status code."""
        error = ReadeckError("Test error", status_code=400)

        assert str(error) == "[400] Test error"
        assert error.status_code == 400

    def test_error_with_response_data(self):
        """Test error with response data."""
        response_data = {"detail": "Invalid request"}
        error = ReadeckError(
            "Validation failed", status_code=422, response_data=response_data
        )

        assert error.response_data == response_data
        assert str(error) == "[422] Validation failed"


class TestReadeckAuthError:
    """Test ReadeckAuthError exception."""

    def test_auth_error_inheritance(self):
        """Test that auth error inherits from ReadeckError."""
        error = ReadeckAuthError("Authentication failed", status_code=401)

        assert isinstance(error, ReadeckError)
        assert str(error) == "[401] Authentication failed"

    def test_auth_error_basic(self):
        """Test basic auth error."""
        error = ReadeckAuthError("Invalid token")

        assert str(error) == "Invalid token"


class TestReadeckNotFoundError:
    """Test ReadeckNotFoundError exception."""

    def test_not_found_error(self):
        """Test not found error."""
        error = ReadeckNotFoundError("Resource not found", status_code=404)

        assert isinstance(error, ReadeckError)
        assert str(error) == "[404] Resource not found"


class TestReadeckValidationError:
    """Test ReadeckValidationError exception."""

    def test_validation_error(self):
        """Test validation error."""
        error = ReadeckValidationError("Invalid data", status_code=422)

        assert isinstance(error, ReadeckError)
        assert str(error) == "[422] Invalid data"


class TestReadeckServerError:
    """Test ReadeckServerError exception."""

    def test_server_error(self):
        """Test server error."""
        error = ReadeckServerError("Internal server error", status_code=500)

        assert isinstance(error, ReadeckError)
        assert str(error) == "[500] Internal server error"
