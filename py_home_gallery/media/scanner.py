"""
Media directory scanning module for Py Home Gallery.

This module contains functions for scanning media directories
and listing available media files.
"""

import os


def list_subfolders(directory):
    """
    List all subfolders in a given directory.
    """
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]


def validate_and_get_folder_path(media_root, folder):
    """
    Validate the folder and return its absolute path.
    If no folder is specified, return the root media directory.
    """
    folder_path = os.path.join(media_root, folder) if folder else media_root
    if folder and (not os.path.exists(folder_path) or not os.path.isdir(folder_path)):
        return None  # Invalid folder
    return folder_path


def scan_directory(directory):
    """
    Recursively scans a directory for media files (images and videos).
    Returns a list of (relative_path, thumbnail_path) tuples.
    """
    media = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.mkv')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=directory)
                
                # For videos, use a separate thumbnail generation logic
                if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    media.append((rel_path, f"/thumbnail/{rel_path}"))
                else:
                    # For images, prepend `/media/` to the path for direct serving
                    media.append((rel_path, f"/media/{rel_path}"))
    return media


def get_sorted_files(media_root, folder_path, sort_by="default"):
    """
    Get files from a folder and optionally sort them.
    Sorting options:
    - "random": Randomize order
    - "new": Sort by newest files first
    - "default": No specific order
    """
    import random
    
    # Get media files from the specified folder
    media = scan_directory(folder_path)
    
    # Sort the media
    if sort_by == "random":
        random.shuffle(media)
    elif sort_by == "new":
        # Use full paths for sorting by modification time to avoid errors
        media = sorted(
            media, 
            key=lambda x: os.path.getmtime(os.path.join(folder_path, x[0])),
            reverse=True
        )
    
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
        print(f"Adjusted media paths for subfolder: {rel_folder}")
    
    return media
