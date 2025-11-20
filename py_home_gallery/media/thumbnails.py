"""
Thumbnail generation module for Py Home Gallery.

This module contains functions for generating thumbnails
for both image and video files.
"""

import os
from typing import Optional
from PIL import Image
from py_home_gallery.utils.security import get_safe_path
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

try:
    # Try the newer style import (may work on newer versions)
    from moviepy.editor import VideoFileClip
    logger.info("Using moviepy.editor import")
except ImportError:
    try:
        # Try the older/alternative style import
        from moviepy import VideoFileClip
        logger.info("Using direct moviepy import")
    except ImportError:
        # Neither import style worked
        logger.error("Failed to import VideoFileClip. Please install moviepy: pip install moviepy>=1.0.0")
        raise ImportError("Failed to import VideoFileClip. Please install moviepy: pip install moviepy>=1.0.0")

def generate_video_thumbnail(video_path: str, thumbnail_path: str, width: int = 300, height: int = 200) -> bool:
    """
    Generate a thumbnail for a video file.
    
    Args:
        video_path: Path to the video file
        thumbnail_path: Path where the thumbnail should be saved
        width: Thumbnail width (default: 300)
        height: Thumbnail height (default: 200)
        
    Returns:
        bool: True if thumbnail was created successfully, False otherwise
    """
    clip = None
    
    try:
        # Validate that video file exists
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False
        
        logger.info(f"Generating thumbnail for: {video_path}")

        # Log file size for monitoring
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.debug(f"Video file size: {file_size_mb:.2f}MB")
        
        # Open the video file
        clip = VideoFileClip(video_path)
        
        # Validate clip duration
        if clip.duration <= 0:
            logger.warning(f"Video has invalid duration: {video_path}")
            clip.close()
            return False
        
        # Take a frame from the middle of the video
        frame_time = min(clip.duration / 2, clip.duration - 0.1)  # Avoid end of video
        frame = clip.get_frame(frame_time)
        
        # Close the video to free resources
        clip.close()
        clip = None

        # Save the frame as a thumbnail
        image = Image.fromarray(frame)
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        # Ensure the directory exists
        thumbnail_dir = os.path.dirname(thumbnail_path)
        if thumbnail_dir:
            os.makedirs(thumbnail_dir, exist_ok=True)
        
        # Save with error handling
        image.save(thumbnail_path, 'PNG', optimize=True)
        
        logger.info(f"Successfully generated thumbnail: {thumbnail_path}")
        return True
    
    except MemoryError:
        logger.error(f"Out of memory while generating thumbnail for: {video_path}")
        return False
    except PermissionError:
        logger.error(f"Permission denied accessing video file: {video_path}")
        return False
    except OSError as e:
        logger.error(f"OS error generating thumbnail for {video_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error generating thumbnail for {video_path}: {e}")
        return False
    finally:
        # Ensure clip is closed even if an error occurred
        if clip is not None:
            try:
                clip.close()
            except Exception as e:
                logger.warning(f"Error closing video clip: {e}")


def ensure_thumbnail_exists(media_root: str, thumbnail_dir: str, filename: str, placeholder_url: Optional[str] = None) -> str:
    """
    Ensure a thumbnail exists for the given media file.
    
    Includes security validation to prevent path traversal attacks.
    
    Args:
        media_root: Root media directory
        thumbnail_dir: Directory where thumbnails are stored
        filename: Relative path to the media file
        placeholder_url: URL to use if thumbnail generation fails
        
    Returns:
        str: Path to the thumbnail or placeholder URL if generation fails
    """
    try:
        # Validate the video path to prevent path traversal
        video_path = get_safe_path(media_root, filename)
        
        if not video_path:
            logger.warning(f"Invalid path for thumbnail generation: {filename}")
            return placeholder_url or ""
        
        # Validate that the file exists
        if not os.path.exists(video_path):
            logger.warning(f"Media file not found for thumbnail: {video_path}")
            return placeholder_url or ""
        
        # Preserve directory structure by using the full relative path
        # Replace path separators with a safe character to avoid issues with nested directories
        safe_filename = filename.replace('\\', '_').replace('/', '_')
        
        # Limit filename length to avoid filesystem issues
        if len(safe_filename) > 200:
            # Use hash for very long filenames
            import hashlib
            file_hash = hashlib.md5(safe_filename.encode()).hexdigest()
            extension = os.path.splitext(safe_filename)[1]
            safe_filename = f"{file_hash}{extension}"
        
        thumbnail_path = os.path.join(thumbnail_dir, f"{safe_filename}.png")
        
        # If thumbnail already exists and is valid, return its path
        if os.path.exists(thumbnail_path):
            # Verify thumbnail is not corrupted (has size > 0)
            if os.path.getsize(thumbnail_path) > 0:
                logger.debug(f"Using existing thumbnail: {thumbnail_path}")
                return thumbnail_path
            else:
                # Remove corrupted thumbnail
                logger.warning(f"Removing corrupted thumbnail: {thumbnail_path}")
                try:
                    os.remove(thumbnail_path)
                except Exception as e:
                    logger.error(f"Error removing corrupted thumbnail: {e}")
        
        # Try to generate the thumbnail
        logger.info(f"Attempting to generate thumbnail for: {filename}")
        if generate_video_thumbnail(video_path, thumbnail_path):
            return thumbnail_path
        
        # Return placeholder if generation fails
        logger.debug(f"Using placeholder for: {filename}")
        return placeholder_url or ""
    
    except Exception as e:
        logger.error(f"Error ensuring thumbnail exists for {filename}: {e}")
        return placeholder_url or ""
