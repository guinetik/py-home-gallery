"""
Media dimension extraction module for Py Home Gallery.

This module provides functions to efficiently extract image and video dimensions
without loading the entire file into memory.
"""

import os
import re
from typing import Tuple, Optional
from PIL import Image
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)


def extract_dimensions_from_filename(filename: str) -> Optional[Tuple[int, int]]:
    """
    Try to extract dimensions from filename patterns like:
    - 1920x1080_abc123.jpg
    - photo_1080x1920.jpg
    - 1200x800.png

    Args:
        filename: The filename to parse

    Returns:
        Optional[Tuple[int, int]]: (width, height) if found, None otherwise
    """
    # Pattern matches: width x height (e.g., 1920x1080, 958x1278)
    pattern = r'(\d{3,5})[xX](\d{3,5})'
    match = re.search(pattern, filename)

    if match:
        width = int(match.group(1))
        height = int(match.group(2))

        # Sanity check: dimensions should be reasonable
        if 10 <= width <= 50000 and 10 <= height <= 50000:
            logger.debug(f"Extracted dimensions from filename {filename}: {width}x{height}")
            return (width, height)

    return None


def get_image_dimensions(image_path: str) -> Optional[Tuple[int, int]]:
    """
    Get dimensions of an image file without loading it entirely.

    PIL can read image headers to get dimensions quickly.

    Args:
        image_path: Path to the image file

    Returns:
        Optional[Tuple[int, int]]: (width, height) or None if failed
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            logger.debug(f"Image dimensions for {os.path.basename(image_path)}: {width}x{height}")
            return (width, height)
    except Exception as e:
        # Use debug level instead of warning to reduce log noise
        logger.debug(f"Could not read image dimensions for {image_path}: {e}")
        return None


def get_video_dimensions(video_path: str, fast_mode: bool = True) -> Optional[Tuple[int, int]]:
    """
    Get dimensions of a video file.

    In fast mode (default), returns standard 16:9 aspect ratio immediately
    without opening the video file. This is much faster for bulk scanning.

    In slow mode, uses moviepy to read actual video metadata.

    Args:
        video_path: Path to the video file
        fast_mode: If True, use default dimensions without opening file (default: True)

    Returns:
        Optional[Tuple[int, int]]: (width, height) or None if failed
    """
    if fast_mode:
        # Fast mode: return common 16:9 HD aspect ratio without opening file
        # This is MUCH faster for bulk operations and still provides correct aspect ratio
        logger.debug(f"Using fast mode for {os.path.basename(video_path)}: 1920x1080")
        return (1920, 1080)

    try:
        # Slow mode: actually open video and read dimensions
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            from moviepy import VideoFileClip

        # Open video and get dimensions
        clip = VideoFileClip(video_path)
        width, height = clip.size
        clip.close()

        logger.debug(f"Video dimensions for {os.path.basename(video_path)}: {width}x{height}")
        return (width, height)

    except Exception as e:
        logger.warning(f"Could not read video dimensions for {video_path}: {e}")
        # Return common 16:9 HD aspect ratio as fallback
        return (1920, 1080)


def get_media_dimensions(file_path: str, fast_mode: bool = True, thumbnail_path: Optional[str] = None) -> Tuple[int, int]:
    """
    Get dimensions of a media file (image or video).

    Uses a fast multi-step approach:
    1. For videos: check if thumbnail exists and use its dimensions
    2. Try extracting from filename (instant)
    3. For images: read PIL headers (fast)
    4. For videos: use defaults (instant)

    Args:
        file_path: Path to the media file
        fast_mode: If True, use fast defaults for videos (default: True)
        thumbnail_path: Optional path to thumbnail file (for videos)

    Returns:
        Tuple[int, int]: (width, height), defaults to 800x600 if all methods fail
    """
    # Check if file exists
    if not os.path.exists(file_path):
        logger.debug(f"File not found: {file_path}")
        return (800, 600)

    # Determine file type by extension
    ext = os.path.splitext(file_path)[1].lower()

    # STEP 1: For videos, if thumbnail exists, use its dimensions (most accurate)
    if ext in ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'):
        if thumbnail_path and os.path.exists(thumbnail_path):
            dims = get_image_dimensions(thumbnail_path)
            if dims:
                logger.debug(f"Using existing thumbnail dimensions for {os.path.basename(file_path)}: {dims}")
                return dims

        # If no thumbnail, try to extract video dimensions from filename
        filename = os.path.basename(file_path)
        dims_from_filename = extract_dimensions_from_filename(filename)
        if dims_from_filename:
            # Scale down to thumbnail size while preserving aspect ratio
            width, height = dims_from_filename
            # Thumbnail max dimensions are 300x200
            if width > height:  # Landscape
                thumb_width = 300
                thumb_height = int(300 * height / width)
            else:  # Portrait or square
                thumb_height = 300
                thumb_width = int(300 * width / height)
            return (thumb_width, thumb_height)

        # Default video thumbnails: assume landscape
        return (300, 169)  # 16:9 aspect ratio scaled to thumbnail size

    # STEP 2: Try extracting from filename (instant, no I/O)
    filename = os.path.basename(file_path)
    dims_from_filename = extract_dimensions_from_filename(filename)
    if dims_from_filename:
        return dims_from_filename

    # STEP 3: Image formats - read actual dimensions (fast with PIL)
    if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'):
        dims = get_image_dimensions(file_path)
        if dims:
            return dims
        # If PIL fails, use common aspect ratios as fallback
        # Default to portrait since many phone photos are portrait
        return (1080, 1920)

    # Default fallback
    logger.debug(f"Using default dimensions for {file_path}")
    return (800, 600)
