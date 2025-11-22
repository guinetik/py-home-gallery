"""
Infinite scrolling route handlers for Py Home Gallery.

This module contains route handlers for the infinite scrolling gallery view.
"""

import os
from typing import List, Tuple
from flask import Blueprint, render_template, request, jsonify, current_app, Response
from py_home_gallery.media.scanner import scan_directory
from py_home_gallery.media.dimension_helper import add_dimensions_to_items
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

# Create a blueprint for infinite scrolling routes
bp = Blueprint('infinite', __name__)

# Global variable to store media metadata
from typing import Dict, Any
media_files: List[Dict[str, Any]] = []


@bp.route('/infinite')
def infinite_gallery() -> str:
    """
    Serve the infinite scrolling gallery page with the initial set of media.
    
    Returns:
        str: Rendered HTML template
    """
    global media_files
    
    try:
        media_root = current_app.config['MEDIA_ROOT']
        items_per_page = current_app.config['ITEMS_PER_PAGE']
        placeholder_url = current_app.config['PLACEHOLDER_URL']

        logger.info("Loading infinite gallery view")
        
        if not media_files:
            logger.info(f"Scanning media directory: {media_root}")
            # Fast scan without dimensions to get file list quickly
            media_files = scan_directory(media_root, use_cache=True, include_dimensions=False)
            logger.info(f"Found {len(media_files)} media files")

        # Sort by newest first with error handling
        try:
            sorted_files = sorted(
                media_files,
                key=lambda x: os.path.getmtime(os.path.join(media_root, x['path'])),
                reverse=True
            )
        except Exception as e:
            logger.error(f"Error sorting files by modification time: {e}")
            sorted_files = media_files

        # Load the first page
        start = 0
        end = items_per_page
        initial_files = sorted_files[start:end]

        # Extract real dimensions ONLY for files on this page
        thumbnail_dir = current_app.config['THUMBNAIL_DIR']
        add_dimensions_to_items(initial_files, media_root, thumbnail_dir)

        return render_template(
            'infinite.html',
            media_files=initial_files,
            placeholder=placeholder_url
        )
    
    except Exception as e:
        logger.error(f"Error in infinite gallery view: {e}")
        return render_template(
            'infinite.html',
            media_files=[],
            placeholder=current_app.config.get('PLACEHOLDER_URL', '')
        )


@bp.route('/gallery-data')
def gallery_data() -> Response:
    """
    Serve paginated media data for infinite scrolling.
    
    Returns:
        Response: JSON response with media data and pagination info
    """
    global media_files
    
    try:
        media_root = current_app.config['MEDIA_ROOT']
        items_per_page = current_app.config['ITEMS_PER_PAGE']
        
        page = int(request.args.get('page', 1))
        sort_by = request.args.get('sort', 'default')  # Default sorting

        logger.debug(f"Gallery data request: page={page}, sort_by={sort_by}")

        if not media_files:
            logger.info(f"Scanning media directory: {media_root}")
            # Fast scan without dimensions to get file list quickly
            media_files = scan_directory(media_root, use_cache=True, include_dimensions=False)
            logger.info(f"Found {len(media_files)} media files")

        # Create a copy for sorting to avoid modifying the global list
        sorted_files = media_files.copy()

        if sort_by == 'new':
            # Sort by last modification time with error handling
            try:
                sorted_files = sorted(
                    sorted_files,
                    key=lambda x: os.path.getmtime(os.path.join(media_root, x['path'])),
                    reverse=True
                )
            except Exception as e:
                logger.error(f"Error sorting files by modification time: {e}")

        start = (page - 1) * items_per_page
        end = start + items_per_page
        media_slice = sorted_files[start:end]
        total_pages = (len(sorted_files) + items_per_page - 1) // items_per_page

        # Extract real dimensions ONLY for files on this page
        thumbnail_dir = current_app.config['THUMBNAIL_DIR']
        add_dimensions_to_items(media_slice, media_root, thumbnail_dir)

        logger.debug(f"Returning {len(media_slice)} items for page {page}")

        return jsonify({
            'media': media_slice,  # Now has path, thumbnail, width, height
            'has_next': page < total_pages
        })
    
    except ValueError as e:
        logger.error(f"Invalid page parameter: {e}")
        return jsonify({'error': 'Invalid page parameter', 'media': [], 'has_next': False}), 400
    except Exception as e:
        logger.error(f"Error in gallery data endpoint: {e}")
        return jsonify({'error': 'Internal server error', 'media': [], 'has_next': False}), 500
