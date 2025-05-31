# Readeck Python Client

A Python client library for the Readeck API, providing easy access to Readeck's bookmark and reading features.

## Features

- Full async/await support
- Type hints with Pydantic models
- Comprehensive error handling
- Support for Python 3.10+
- Easy authentication with Bearer tokens

## Installation

```bash
pip install readeck
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

    # Create a bookmark
    result = await client.create_bookmark(
        url="https://example.com/article",
        title="Interesting Article",
        labels=["reading", "tech"]
    )
    print(f"Bookmark created with ID: {result.bookmark_id}")

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

### Bookmarks

#### Create Bookmark

Create a new bookmark:

```python
# Minimal bookmark
result = await client.create_bookmark(url="https://example.com")

# Bookmark with title
result = await client.create_bookmark(
    url="https://example.com/article",
    title="Article Title"
)

# Bookmark with labels
result = await client.create_bookmark(
    url="https://example.com/tutorial",
    labels=["tutorial", "programming"]
)

# Complete bookmark
result = await client.create_bookmark(
    url="https://example.com/complete",
    title="Complete Example",
    labels=["example", "complete", "demo"]
)
```

The `create_bookmark` method returns a `BookmarkCreateResult` object containing:
- `response`: The API response with message and status
- `bookmark_id`: The ID of the created bookmark (from response headers)
- `location`: The URL of the created resource (from response headers)

#### Get Bookmarks

Retrieve bookmarks with optional filtering:

```python
# Get all bookmarks
bookmarks = await client.get_bookmarks()

# Get bookmarks with parameters
from readeck import BookmarkListParams

params = BookmarkListParams(
    limit=10,
    search="python",
    labels="programming"
)
bookmarks = await client.get_bookmarks(params)
```

#### Export Bookmarks

Export bookmarks in different formats:

```python
bookmark_id = "some_bookmark_id"

# Export as markdown (default format)
markdown_content = await client.export_bookmark(bookmark_id)

# Export as markdown explicitly
markdown_content = await client.export_bookmark(bookmark_id, format="md")

# Export as EPUB
epub_content = await client.export_bookmark(bookmark_id, format="epub")

# Save to files
with open("article.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)

with open("article.epub", "wb") as f:
    f.write(epub_content)
```

Supported export formats:
- `md` (markdown) - Returns a string with the article content as markdown
- `epub` - Returns bytes containing the EPUB file data

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
