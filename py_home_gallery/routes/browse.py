"""
Browse route handler for Py Home Gallery.

This module contains route handler for the browse view
which allows folder-based navigation.
"""

import os
import random
from flask import Blueprint, render_template, jsonify, current_app
from py_home_gallery.media.scanner import list_subfolders, scan_directory
from py_home_gallery.media.utils import is_image
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

# Create a blueprint for browse routes
bp = Blueprint('browse', __name__)


@bp.route('/browse')
def browse():
    """Browse view - folder-based navigation."""
    return render_template('browse.html')


@bp.route('/api/browse')
def browse_api():
    """
    API endpoint that returns all subfolders with a random vertical thumbnail.

    Returns:
        JSON response with list of folders, each containing:
        - folder: folder name
        - thumbnail: path to a random vertical image thumbnail
        - count: number of media files in the folder
    """
    media_root = current_app.config['MEDIA_ROOT']

    try:
        # Get all subfolders in media root
        subfolders = list_subfolders(media_root)
        logger.info(f"Found {len(subfolders)} subfolders in {media_root}")

        result = []

        for folder_name in subfolders:
            folder_path = os.path.join(media_root, folder_name)

            # Scan the folder for media files (with dimensions)
            media_files = scan_directory(folder_path, use_cache=True, include_dimensions=True)

            if not media_files:
                logger.debug(f"No media files in folder: {folder_name}")
                continue

            # Filter for vertical images only (height > width)
            vertical_images = [
                item for item in media_files
                if is_image(item['path']) and item.get('height', 0) > item.get('width', 0)
            ]

            # If no vertical images, fall back to any image
            if not vertical_images:
                logger.debug(f"No vertical images in {folder_name}, using any image")
                vertical_images = [
                    item for item in media_files
                    if is_image(item['path'])
                ]

            # If still no images, skip this folder
            if not vertical_images:
                logger.debug(f"No images at all in folder: {folder_name}")
                continue

            # Pick a random vertical image
            random_image = random.choice(vertical_images)

            result.append({
                'folder': folder_name,
                'thumbnail': random_image['thumbnail'],
                'count': len(media_files),
                'width': random_image.get('width', 300),
                'height': random_image.get('height', 400)
            })

        logger.info(f"Returning {len(result)} folders with thumbnails")

        return jsonify({
            'success': True,
            'folders': result
        })

    except Exception as e:
        logger.error(f"Error in browse API: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
