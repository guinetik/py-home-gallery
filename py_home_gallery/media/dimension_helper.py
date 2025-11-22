"""
Helper functions for extracting media dimensions.
"""

import os
import hashlib
from typing import List, Dict, Any
from py_home_gallery.media.dimensions import get_media_dimensions


def add_dimensions_to_items(items: List[Dict[str, Any]], media_root: str, thumbnail_dir: str) -> None:
    """
    Add width and height dimensions to media items.

    Modifies items in-place by adding 'width' and 'height' keys.
    For videos, checks if thumbnail exists and uses its dimensions.

    Args:
        items: List of media item dictionaries (modified in-place)
        media_root: Root media directory path
        thumbnail_dir: Directory where thumbnails are stored
    """
    for item in items:
        full_path = os.path.join(media_root, item['path'])

        # For videos, pass thumbnail path so we can use its dimensions if it exists
        thumbnail_path = None
        if item['path'].lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv')):
            safe_filename = item['path'].replace('\\', '_').replace('/', '_')

            # Handle very long filenames
            if len(safe_filename) > 200:
                file_hash = hashlib.md5(safe_filename.encode()).hexdigest()
                extension = os.path.splitext(safe_filename)[1]
                safe_filename = f"{file_hash}{extension}"

            thumbnail_path = os.path.join(thumbnail_dir, f"{safe_filename}.png")

        # Extract dimensions
        width, height = get_media_dimensions(full_path, thumbnail_path=thumbnail_path)
        item['width'] = width
        item['height'] = height
