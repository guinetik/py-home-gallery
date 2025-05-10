"""
Media serving routes for Py Home Gallery.

This module contains route handlers for serving media files,
including original media and thumbnails.
"""

import os
from flask import Blueprint, send_file, current_app, abort
from py_home_gallery.media.thumbnails import ensure_thumbnail_exists

# Create a blueprint for media routes
bp = Blueprint('media', __name__)


@bp.route('/thumbnail/<path:filename>')
def serve_thumbnail(filename):
    """
    Serve generated thumbnails for videos, creating them on-demand if missing.
    """
    media_root = current_app.config['MEDIA_ROOT']
    thumbnail_dir = current_app.config['THUMBNAIL_DIR']
    placeholder_url = current_app.config['PLACEHOLDER_URL']
    
    # Ensure thumbnail exists or return placeholder
    thumbnail_path = ensure_thumbnail_exists(
        media_root, 
        thumbnail_dir, 
        filename, 
        placeholder_url
    )
    
    # If we got a placeholder URL, redirect to it
    if thumbnail_path == placeholder_url:
        return thumbnail_path
    
    # Otherwise, serve the thumbnail file
    return send_file(thumbnail_path)


@bp.route('/media/<path:filename>')
def serve_media(filename):
    """
    Serve media files.
    """
    media_root = current_app.config['MEDIA_ROOT']
    file_path = os.path.join(media_root, filename)
    
    # Debug logging
    print(f"Attempting to serve file: {file_path}")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        # Check if there's a similar file in any of the subdirectories
        for root, _, files in os.walk(media_root):
            for file in files:
                if os.path.basename(file) == os.path.basename(filename):
                    correct_path = os.path.join(root, file)
                    print(f"Found similar file at: {correct_path}")
                    return send_file(correct_path)
        
        # If we get here, no matching file was found
        return abort(404, description=f"File not found: {filename}")
    
    return send_file(file_path)
