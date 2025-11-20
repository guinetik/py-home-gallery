"""
Media utility functions for Py Home Gallery.

This module contains utility functions for handling media files,
including file type detection and path handling.
"""

import os
from typing import Literal


def is_image(filename: str) -> bool:
    """
    Check if a file is an image based on its extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the file is an image, False otherwise
    """
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))


def is_video(filename: str) -> bool:
    """
    Check if a file is a video based on its extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the file is a video, False otherwise
    """
    return filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'))


def is_media(filename: str) -> bool:
    """
    Check if a file is a supported media file (image or video).
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the file is a supported media file, False otherwise
    """
    return is_image(filename) or is_video(filename)


def get_media_type(filename: str) -> Literal['image', 'video', 'unknown']:
    """
    Get the media type of a file.
    
    Args:
        filename: The filename to check
        
    Returns:
        str: 'image', 'video', or 'unknown'
    """
    if is_image(filename):
        return 'image'
    elif is_video(filename):
        return 'video'
    else:
        return 'unknown'


def get_thumbnail_url(filename: str, media_root: str) -> str:
    """
    Get the URL for a file's thumbnail.
    
    Args:
        filename: The filename
        media_root: The root media directory
        
    Returns:
        str: URL for the thumbnail
    """
    if is_video(filename):
        return f"/thumbnail/{os.path.relpath(filename, start=media_root)}"
    else:
        return f"/media/{os.path.relpath(filename, start=media_root)}"
