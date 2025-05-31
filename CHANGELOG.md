# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2025-05-31

### Added
- `export_bookmark_parsed()` - Markdown frontmatter parsing to metadata

## [0.1.3] - 2025-05-31

### Added
- Scripts to simplify changelog
- export_bookmark() - Bookmark Export API

## [0.1.2] - 2024-12-31

### Added
- Initial release of Readeck Python client
- Async/await support for all API operations
- Full type hints with Pydantic models
- Comprehensive error handling
- User profile management
- Bookmark operations (list, create, get details, export)
- Support for bookmark export in multiple formats (Markdown, EPUB)
- Bearer token authentication
- Python 3.10+ support

### Features
- `ReadeckClient` - Main client class for API interactions
- `get_profile()` - Retrieve user profile information
- `list_bookmarks()` - List bookmarks with filtering and pagination
- `create_bookmark()` - Create new bookmarks from URLs
- `get_bookmark()` - Get detailed bookmark information

### Error Handling
- `ReadeckError` - Base exception class
- `ReadeckAuthError` - Authentication and authorization errors
- `ReadeckNotFoundError` - Resource not found errors
- `ReadeckServerError` - Server-side errors
- `ReadeckValidationError` - Input validation errors
