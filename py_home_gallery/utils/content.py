"""
Content Management System

This module handles loading and managing customizable content for the gallery.
Content can be customized via content.json file in the application root.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

# Default content (fallback if content.json is not found or incomplete)
DEFAULT_CONTENT: Dict[str, Any] = {
    "site": {
        "title": "Py Home Gallery",
        "description": "A lightweight media gallery server for your home network"
    },
    "navigation": {
        "logo_alt": "Logo",
        "site_name": "Py Home Gallery"
    },
    "home": {
        "hero_title": "Your Media Collection",
        "hero_subtitle": "Browse, discover, and enjoy your photos and videos",
        "stats": {
            "total_files": "Total Files",
            "images": "Images",
            "videos": "Videos",
            "folders": "Folders"
        }
    },
    "views": {
        "browse": {
            "title": "Browse",
            "description": "Navigate through your media folders",
            "icon": "📂"
        },
        "gallery": {
            "title": "Gallery",
            "description": "Explore your entire collection with classic pagination",
            "icon": "🖼️"
        },
        "shuffle": {
            "title": "Shuffle",
            "description": "Discover random media from your library",
            "icon": "🎲"
        },
        "newest": {
            "title": "Newest",
            "description": "See your most recently added media first",
            "icon": "⭐"
        },
        "infinite": {
            "title": "Infinite Scroll",
            "description": "Endless browsing experience - new content loads as you scroll",
            "icon": "∞"
        }
    },
    "gallery_page": {
        "title": "Gallery",
        "all_folders": "All Folders",
        "all_media": "All Media",
        "images_only": "Images Only",
        "videos_only": "Videos Only"
    },
    "browse_page": {
        "title": "Browse Folders",
        "subtitle": "Navigate through your media collection",
        "loading": "Loading folders...",
        "no_folders": "No folders found",
        "item_count": {
            "singular": "item",
            "plural": "items"
        }
    }
}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with override values taking precedence.

    Args:
        base: Base dictionary with default values
        override: Dictionary with override values

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_content(content_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load content from multiple sources (priority order):
    1. PY_HOME_GALLERY_CONTENT_JSON environment variable (JSON string)
    2. content.json file (from content_path, current dir, or project root)
    3. Default content

    Args:
        content_path: Optional path to content.json file.
                     If not provided, looks in current directory and project root.

    Returns:
        Dictionary containing all content strings
    """
    content = DEFAULT_CONTENT.copy()
    loaded = False

    # Priority 1: Check for JSON content in environment variable
    content_json_env = os.environ.get('PY_HOME_GALLERY_CONTENT_JSON')
    if content_json_env:
        try:
            logger.info("Loading custom content from PY_HOME_GALLERY_CONTENT_JSON environment variable")
            custom_content = json.loads(content_json_env)
            content = deep_merge(DEFAULT_CONTENT, custom_content)
            loaded = True
            logger.info("Custom content from environment variable loaded successfully")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PY_HOME_GALLERY_CONTENT_JSON: {e}")
        except Exception as e:
            logger.error(f"Error loading content from environment variable: {e}")

    # Priority 2: Try loading from file paths (if not loaded from env var)
    if not loaded:
        paths_to_try = []

        if content_path:
            paths_to_try.append(Path(content_path))

        # Try current working directory
        paths_to_try.append(Path.cwd() / "content.json")

        # Try project root (parent of py_home_gallery package)
        try:
            package_dir = Path(__file__).parent.parent.parent
            paths_to_try.append(package_dir / "content.json")
        except Exception:
            pass

        # Try to load from each path
        for path in paths_to_try:
            try:
                if path.exists() and path.is_file():
                    logger.info(f"Loading custom content from: {path}")
                    with open(path, 'r', encoding='utf-8') as f:
                        custom_content = json.load(f)

                    # Deep merge custom content with defaults
                    content = deep_merge(DEFAULT_CONTENT, custom_content)
                    loaded = True
                    logger.info("Custom content loaded successfully")
                    break
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse content.json at {path}: {e}")
            except Exception as e:
                logger.error(f"Error loading content from {path}: {e}")

    if not loaded:
        logger.info("No custom content found, using default content")

    return content


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "home.hero_title")
        default: Default value if path not found

    Returns:
        Value at the path, or default if not found

    Example:
        >>> content = {"home": {"hero_title": "Welcome"}}
        >>> get_nested_value(content, "home.hero_title")
        "Welcome"
    """
    keys = path.split('.')
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


class ContentManager:
    """
    Manager for accessing content throughout the application.
    """

    def __init__(self, content_path: Optional[str] = None):
        """
        Initialize content manager.

        Args:
            content_path: Optional path to content.json file
        """
        self._content = load_content(content_path)

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get content value by path.

        Args:
            path: Dot-separated path (e.g., "home.hero_title")
            default: Default value if not found

        Returns:
            Content value
        """
        return get_nested_value(self._content, path, default)

    def get_all(self) -> Dict[str, Any]:
        """
        Get all content.

        Returns:
            Complete content dictionary
        """
        return self._content.copy()

    def reload(self, content_path: Optional[str] = None) -> None:
        """
        Reload content from file.

        Args:
            content_path: Optional path to content.json file
        """
        self._content = load_content(content_path)
        logger.info("Content reloaded")


# Global content manager instance
_content_manager: Optional[ContentManager] = None


def get_content_manager(content_path: Optional[str] = None) -> ContentManager:
    """
    Get or create the global content manager instance.

    Args:
        content_path: Optional path to content.json file

    Returns:
        ContentManager instance
    """
    global _content_manager

    if _content_manager is None:
        _content_manager = ContentManager(content_path)

    return _content_manager


def get_content(path: Optional[str] = None, default: Any = None) -> Any:
    """
    Convenience function to get content value.

    Args:
        path: Dot-separated path (e.g., "home.hero_title").
             If None, returns all content.
        default: Default value if path not found

    Returns:
        Content value or all content
    """
    manager = get_content_manager()

    if path is None:
        return manager.get_all()

    return manager.get(path, default)
