# Changelog Management

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format for tracking changes.

## Structure

The changelog is organized into sections:

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Adding Entries

### Manual Method

Edit `CHANGELOG.md` directly and add entries under the `## [Unreleased]` section in the appropriate subsection.

### Using the Script

Use the provided script for easier management:

```bash
# Add a new feature
python scripts/changelog.py add added "New bookmark export feature"

# Add a bug fix
python scripts/changelog.py add fixed "Fixed authentication error handling"

# Add a security fix
python scripts/changelog.py add security "Fixed potential XSS vulnerability"
```

## Preparing a Release

When ready to release a new version:

1. Run the changelog script with the new version number:
   ```bash
   python scripts/changelog.py release 0.2.0
   ```
2. Review the changes (the script automatically updates both `CHANGELOG.md` and `src/readeck/__init__.py`)
3. Commit the changes
4. Create a GitHub release with the version number

The script will automatically:
- Move all unreleased items to a new version section with today's date in `CHANGELOG.md`
- Update the `__version__` variable in `src/readeck/__init__.py` to match the release version
