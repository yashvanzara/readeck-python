#!/usr/bin/env python3
"""
Changelog management script for Readeck Python client.

This script helps maintain the CHANGELOG.md file by providing utilities
to add new entries and prepare for releases.
"""

import argparse
import re
from datetime import date
from pathlib import Path


def read_changelog(changelog_path: Path) -> str:
    """Read the current changelog content."""
    return changelog_path.read_text()


def add_entry(changelog_path: Path, entry_type: str, description: str) -> None:
    """Add a new entry to the Unreleased section."""
    content = read_changelog(changelog_path)

    # Find the Unreleased section
    unreleased_pattern = r"(## \[Unreleased\].*?)(## \[)"
    match = re.search(unreleased_pattern, content, re.DOTALL)

    if not match:
        print("Could not find Unreleased section in changelog")
        return

    unreleased_section = match.group(1)

    # Check if the entry type section exists
    entry_type_pattern = f"### {entry_type.title()}"
    if entry_type_pattern not in unreleased_section:
        # Add the section after "## [Unreleased]"
        new_section = f"\n\n### {entry_type.title()}\n- {description}"
        unreleased_section = unreleased_section.replace(
            "## [Unreleased]", f"## [Unreleased]{new_section}"
        )
    else:
        # Add to existing section
        section_pattern = f"(### {entry_type.title()}\n)(.*?)(?=\n### |\n## |$)"
        section_match = re.search(section_pattern, unreleased_section, re.DOTALL)
        if section_match:
            existing_entries = section_match.group(2).strip()
            new_entries = (
                f"{existing_entries}\n- {description}"
                if existing_entries
                else f"- {description}"
            )
            unreleased_section = unreleased_section.replace(
                section_match.group(0), f"{section_match.group(1)}{new_entries}\n"
            )

    # Replace in the full content
    new_content = content.replace(match.group(1), unreleased_section)
    changelog_path.write_text(new_content)
    print(f"Added {entry_type} entry: {description}")


def update_version_in_init(version: str) -> None:
    """Update the version in __init__.py file."""
    init_path = Path("src/readeck/__init__.py")

    if not init_path.exists():
        print("Warning: src/readeck/__init__.py not found")
        return

    content = init_path.read_text()

    # Update the __version__ line
    version_pattern = r'__version__ = "[^"]*"'
    new_version_line = f'__version__ = "{version}"'

    if re.search(version_pattern, content):
        content = re.sub(version_pattern, new_version_line, content)
        init_path.write_text(content)
        print(f"Updated version in __init__.py to {version}")
    else:
        print("Warning: Could not find __version__ line in __init__.py")


def prepare_release(changelog_path: Path, version: str) -> None:
    """Prepare the changelog for a new release and update version in __init__.py."""
    content = read_changelog(changelog_path)
    today = date.today().strftime("%Y-%m-%d")

    # Replace [Unreleased] with the new version
    content = content.replace(
        "## [Unreleased]", f"## [Unreleased]\n\n## [{version}] - {today}"
    )

    changelog_path.write_text(content)
    print(f"Prepared changelog for release {version}")

    # Also update version in __init__.py
    update_version_in_init(version)


def main():
    """Manage the project changelog via command-line interface.

    Provides a command-line interface to add new changelog entries and prepare
    releases by moving unreleased changes to a versioned section.
    """
    parser = argparse.ArgumentParser(description="Manage the project changelog")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add entry command
    add_parser = subparsers.add_parser("add", help="Add a new changelog entry")
    add_parser.add_argument(
        "type",
        choices=["added", "changed", "deprecated", "removed", "fixed", "security"],
        help="Type of change",
    )
    add_parser.add_argument("description", help="Description of the change")

    # Prepare release command
    release_parser = subparsers.add_parser(
        "release", help="Prepare changelog for release"
    )
    release_parser.add_argument("version", help="Version number (e.g., 0.2.0)")

    args = parser.parse_args()

    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print("CHANGELOG.md not found in current directory")
        return

    if args.command == "add":
        add_entry(changelog_path, args.type, args.description)
    elif args.command == "release":
        prepare_release(changelog_path, args.version)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
