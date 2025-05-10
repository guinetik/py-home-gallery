"""
Infinite scrolling route handlers for Py Home Gallery.

This module contains route handlers for the infinite scrolling gallery view.
"""

import os
from flask import Blueprint, render_template, request, jsonify, current_app
from py_home_gallery.media.scanner import scan_directory

# Create a blueprint for infinite scrolling routes
bp = Blueprint('infinite', __name__)

# Global variable to store media metadata
media_files = []


@bp.route('/infinite')
def infinite_gallery():
    """
    Serve the infinite scrolling gallery page with the initial set of media.
    """
    global media_files
    media_root = current_app.config['MEDIA_ROOT']
    items_per_page = current_app.config['ITEMS_PER_PAGE']
    placeholder_url = current_app.config['PLACEHOLDER_URL']

    if not media_files:
        media_files = scan_directory(media_root)

    # Sort by newest first
    sorted_files = sorted(
        media_files, 
        key=lambda x: os.path.getmtime(os.path.join(media_root, x[0])), 
        reverse=True
    )

    # Load the first page
    start = 0
    end = items_per_page
    initial_files = sorted_files[start:end]

    return render_template(
        'infinite.html',
        media_files=initial_files,
        placeholder=placeholder_url
    )


@bp.route('/gallery-data')
def gallery_data():
    """
    Serve paginated media data for infinite scrolling.
    """
    global media_files
    media_root = current_app.config['MEDIA_ROOT']
    items_per_page = current_app.config['ITEMS_PER_PAGE']
    
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort', 'default')  # Default sorting

    if not media_files:
        media_files = scan_directory(media_root)

    if sort_by == 'new':
        # Sort by last modification time
        media_files = sorted(
            media_files, 
            key=lambda x: os.path.getmtime(os.path.join(media_root, x[0])), 
            reverse=True
        )

    start = (page - 1) * items_per_page
    end = start + items_per_page
    media_slice = media_files[start:end]
    total_pages = (len(media_files) + items_per_page - 1) // items_per_page

    return jsonify({
        'media': [{'path': media, 'thumbnail': thumbnail} for media, thumbnail in media_slice],
        'has_next': page < total_pages
    })
