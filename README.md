# Readeck Python Client

A Python client library for the Readeck API, providing easy access to Readeck's bookmark and reading features.

## Features

- Full async/await support
- Type hints with Pydantic models
- Comprehensive error handling
- Support for Python 3.8+
- Easy authentication with Bearer tokens

## Installation

```bash
pip install readeck-python
```

## Quick Start

```python
import asyncio
from readeck import ReadeckClient

async def main():
    client = ReadeckClient(
        base_url="https://your-readeck-instance.com",
        token="your-bearer-token"
    )

    # Get user profile
    profile = await client.get_user_profile()
    print(f"Welcome, {profile.user.username}!")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

The client uses Bearer token authentication. You can obtain your token from your Readeck instance's settings.

```python
client = ReadeckClient(
    base_url="https://your-readeck-instance.com",
    token="your-bearer-token"
)
```

## API Reference

### User Profile

Get the current user's profile information:

```python
profile = await client.get_user_profile()
```

Returns a `UserProfile` object containing:
- User information (username, email, creation date)
- Authentication provider details
- User settings and preferences
- Reader settings (font, font size, line height)

## Development

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run black src tests
uv run isort src tests
uv run flake8 src tests
uv run mypy src

# Run all checks
uv run pre-commit run --all-files
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
