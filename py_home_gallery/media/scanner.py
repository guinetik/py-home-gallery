"""
Media directory scanning module for Py Home Gallery.

This module contains functions for scanning media directories
and listing available media files.
"""

import os
from typing import List, Tuple, Optional
from py_home_gallery.utils.security import get_safe_path, validate_media_extension
from py_home_gallery.utils.logger import get_logger
from py_home_gallery.utils.cache import get_directory_cache, cache_key_for_directory

logger = get_logger(__name__)
directory_cache = get_directory_cache()


def list_subfolders(directory: str) -> List[str]:
    """
    List all subfolders in a given directory.
    
    Args:
        directory: Path to the directory to scan
        
    Returns:
        List[str]: List of subfolder names
    """
    try:
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            return []
        
        if not os.path.isdir(directory):
            logger.warning(f"Path is not a directory: {directory}")
            return []
        
        subfolders = []
        for name in os.listdir(directory):
            folder_path = os.path.join(directory, name)
            if os.path.isdir(folder_path):
                subfolders.append(name)
        
        return subfolders
    except PermissionError:
        logger.error(f"Permission denied accessing directory: {directory}")
        return []
    except Exception as e:
        logger.error(f"Error listing subfolders in {directory}: {e}")
        return []


def validate_and_get_folder_path(media_root: str, folder: Optional[str]) -> Optional[str]:
    """
    Validate the folder and return its absolute path.
    If no folder is specified, return the root media directory.
    
    This function includes path traversal attack protection.
    
    Args:
        media_root: Root media directory path
        folder: Optional subfolder name/path
        
    Returns:
        Optional[str]: Validated absolute path, or None if invalid
    """
    try:
        # If no folder specified, return media root
        if not folder:
            return os.path.abspath(media_root)
        
        # Use safe path validation to prevent path traversal
        folder_path = get_safe_path(media_root, folder)
        
        if not folder_path:
            logger.warning(f"Path traversal attempt detected: {folder}")
            return None
        
        # Check if path exists and is a directory
        if not os.path.exists(folder_path):
            logger.warning(f"Folder does not exist: {folder_path}")
            return None
        
        if not os.path.isdir(folder_path):
            logger.warning(f"Path is not a directory: {folder_path}")
            return None
        
        return folder_path
    
    except Exception as e:
        logger.error(f"Error validating folder path: {e}")
        return None


def scan_directory(directory: str, use_cache: bool = True) -> List[Tuple[str, str]]:
    """
    Recursively scans a directory for media files (images and videos).
    Returns a list of (relative_path, thumbnail_path) tuples.
    
    Uses caching to improve performance on repeated scans.
    
    Args:
        directory: Path to the directory to scan
        use_cache: Whether to use cache (default: True)
        
    Returns:
        List[Tuple[str, str]]: List of (relative_path, thumbnail_path) tuples
    """
    # Try to get from cache first
    if use_cache:
        cache_key = cache_key_for_directory(directory)
        cached_result = directory_cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Using cached scan result for: {directory} ({len(cached_result)} files)")
            return cached_result
    
    media = []
    scanned_files = 0
    skipped_files = 0
    errors = 0
    
    logger.info(f"Starting directory scan: {directory}")
    
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                scanned_files += 1
                
                try:
                    # Validate file extension
                    if not validate_media_extension(file):
                        skipped_files += 1
                        continue
                    
                    full_path = os.path.join(root, file)
                    
                    # Validate that the file is accessible
                    if not os.path.exists(full_path):
                        logger.warning(f"File not found (broken symlink?): {full_path}")
                        errors += 1
                        continue
                    
                    # Check if we can read the file
                    if not os.access(full_path, os.R_OK):
                        logger.warning(f"File not readable (permission denied): {full_path}")
                        errors += 1
                        continue
                    
                    rel_path = os.path.relpath(full_path, start=directory)
                    
                    # For videos, use a separate thumbnail generation logic
                    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv')):
                        media.append((rel_path, f"/thumbnail/{rel_path}"))
                    else:
                        # For images, prepend `/media/` to the path for direct serving
                        media.append((rel_path, f"/media/{rel_path}"))
                
                except PermissionError:
                    logger.warning(f"Permission denied accessing file: {file}")
                    errors += 1
                    continue
                except Exception as e:
                    logger.error(f"Error processing file {file}: {e}")
                    errors += 1
                    continue
    
    except PermissionError as e:
        logger.error(f"Permission denied accessing directory: {directory}")
        raise
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        raise
    
    logger.info(f"Scan complete: {len(media)} media files found, "
                f"{scanned_files} files scanned, {skipped_files} skipped, {errors} errors")
    
    # Cache the result
    if use_cache and media:
        cache_key = cache_key_for_directory(directory)
        directory_cache.set(cache_key, media)
        logger.debug(f"Cached scan result for: {directory}")
    
    return media


def get_sorted_files(media_root: str, folder_path: str, sort_by: str = "default", use_cache: bool = True) -> List[Tuple[str, str]]:
    """
    Get files from a folder and optionally sort them.
    
    Args:
        media_root: Root media directory
        folder_path: Specific folder to scan
        sort_by: Sorting method - "random", "new", or "default"
        use_cache: Whether to use cache (default: True)
        
    Returns:
        List[Tuple[str, str]]: List of (relative_path, thumbnail_path) tuples
        
    Sorting options:
        - "random": Randomize order
        - "new": Sort by newest files first
        - "default": No specific order
    """
    import random
    
    logger.info(f"Getting sorted files from {folder_path} with sort_by={sort_by}")
    
    try:
        # Get media files from the specified folder (with caching)
        media = scan_directory(folder_path, use_cache=use_cache)
        
        # Sort the media
        if sort_by == "random":
            random.shuffle(media)
            logger.debug(f"Randomized {len(media)} media files")
        elif sort_by == "new":
            # Use full paths for sorting by modification time to avoid errors
            try:
                media = sorted(
                    media, 
                    key=lambda x: os.path.getmtime(os.path.join(folder_path, x[0])),
                    reverse=True
                )
                logger.debug(f"Sorted {len(media)} media files by modification time")
            except Exception as e:
                logger.error(f"Error sorting files by modification time: {e}")
                # Continue with unsorted media
        
        # If folder_path is not media_root, adjust the paths to be relative to media_root
        if folder_path != media_root:
            rel_folder = os.path.relpath(folder_path, start=media_root)
            
            # Prepend the folder path to the relative paths
            adjusted_media = []
            for path, thumb_path in media:
                if thumb_path.startswith('/thumbnail/'):
                    adjusted_thumb = f"/thumbnail/{os.path.join(rel_folder, path)}"
                else:
                    adjusted_thumb = f"/media/{os.path.join(rel_folder, path)}"
                
                adjusted_media.append((os.path.join(rel_folder, path), adjusted_thumb))
            
            media = adjusted_media
            logger.debug(f"Adjusted media paths for subfolder: {rel_folder}")
        
        return media
    
    except Exception as e:
        logger.error(f"Error getting sorted files: {e}")
        return []
