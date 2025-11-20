"""
Security utilities for Py Home Gallery.

This module provides security functions to prevent path traversal attacks
and validate file access within allowed directories.
"""

import os
from typing import Optional
from pathlib import Path


def is_safe_path(base_dir: str, user_path: str, follow_symlinks: bool = False) -> bool:
    """
    Validate that a user-provided path is within the base directory.
    
    Protects against path traversal attacks (e.g., ../../etc/passwd).
    
    Args:
        base_dir: The base directory that should contain the file
        user_path: The user-provided path to validate
        follow_symlinks: Whether to resolve symbolic links (default: False)
        
    Returns:
        bool: True if the path is safe, False otherwise
        
    Examples:
        >>> is_safe_path('/media', '/media/photos/img.jpg')
        True
        >>> is_safe_path('/media', '/media/../etc/passwd')
        False
    """
    # Resolve to absolute paths
    if follow_symlinks:
        base_dir = os.path.realpath(base_dir)
        user_path = os.path.realpath(user_path)
    else:
        base_dir = os.path.abspath(base_dir)
        user_path = os.path.abspath(user_path)
    
    # Check if user_path starts with base_dir
    # Use os.path.commonpath to avoid issues with similar prefixes
    try:
        common_path = os.path.commonpath([base_dir, user_path])
        return common_path == base_dir
    except ValueError:
        # Paths are on different drives (Windows)
        return False


def get_safe_path(base_dir: str, relative_path: str, follow_symlinks: bool = False) -> Optional[str]:
    """
    Safely join a base directory with a relative path and validate the result.
    
    Args:
        base_dir: The base directory
        relative_path: The relative path to join
        follow_symlinks: Whether to resolve symbolic links (default: False)
        
    Returns:
        str: The safe absolute path, or None if the path is invalid
        
    Examples:
        >>> get_safe_path('/media', 'photos/img.jpg')
        '/media/photos/img.jpg'
        >>> get_safe_path('/media', '../etc/passwd')
        None
    """
    if not relative_path:
        return os.path.abspath(base_dir)
    
    # Join paths
    full_path = os.path.join(base_dir, relative_path)
    
    # Validate the result
    if is_safe_path(base_dir, full_path, follow_symlinks):
        return full_path
    
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potentially dangerous characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: The sanitized filename
        
    Examples:
        >>> sanitize_filename('../../etc/passwd')
        'etcpasswd'
        >>> sanitize_filename('photo<script>.jpg')
        'photoscript.jpg'
    """
    # Remove path separators and dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*', '\0']
    
    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized


def validate_media_extension(filename: str, allowed_extensions: tuple = None) -> bool:
    """
    Validate that a file has an allowed media extension.
    
    Args:
        filename: The filename to validate
        allowed_extensions: Tuple of allowed extensions (default: common media types)
        
    Returns:
        bool: True if the extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = (
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp',  # Images
            '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'   # Videos
        )
    
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in allowed_extensions)

