"""
Thumbnail generation module for Py Home Gallery.

This module contains functions for generating thumbnails
for both image and video files.
"""

import os
from PIL import Image
try:
    # Try the newer style import (may work on newer versions)
    from moviepy.editor import VideoFileClip
    print("Using moviepy.editor import")
except ImportError:
    try:
        # Try the older/alternative style import
        from moviepy import VideoFileClip
        print("Using direct moviepy import")
    except ImportError:
        # Neither import style worked
        raise ImportError("Failed to import VideoFileClip. Please install moviepy: pip install moviepy>=1.0.0")

def generate_video_thumbnail(video_path, thumbnail_path, width=300, height=200):
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
    try:
        # Open the video file
        clip = VideoFileClip(video_path)
        
        # Take a frame from the middle of the video
        frame = clip.get_frame(clip.duration / 2)
        
        # Close the video to free resources
        clip.close()

        # Save the frame as a thumbnail
        image = Image.fromarray(frame)
        image.thumbnail((width, height))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        image.save(thumbnail_path)
        
        return True
    except Exception as e:
        print(f"Error generating thumbnail for {video_path}: {e}")
        return False


def ensure_thumbnail_exists(media_root, thumbnail_dir, filename, placeholder_url=None):
    """
    Ensure a thumbnail exists for the given media file.
    
    Args:
        media_root: Root media directory
        thumbnail_dir: Directory where thumbnails are stored
        filename: Relative path to the media file
        placeholder_url: URL to use if thumbnail generation fails
        
    Returns:
        str: Path to the thumbnail or placeholder URL if generation fails
    """
    video_path = os.path.join(media_root, filename)
    
    # Preserve directory structure by using the full relative path
    # Replace path separators with a safe character to avoid issues with nested directories
    safe_filename = filename.replace('\\', '_').replace('/', '_')
    thumbnail_path = os.path.join(thumbnail_dir, f"{safe_filename}.png")
    
    # If thumbnail already exists, return its path
    if os.path.exists(thumbnail_path):
        return thumbnail_path
    
    # Try to generate the thumbnail
    if generate_video_thumbnail(video_path, thumbnail_path):
        return thumbnail_path
    
    # Return placeholder if generation fails
    return placeholder_url
