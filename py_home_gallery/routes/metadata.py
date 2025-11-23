"""
Metadata API routes for Py Home Gallery.

This module provides API endpoints for retrieving media metadata.
"""

from flask import Blueprint, jsonify, current_app, make_response, request
from py_home_gallery.utils.metadata import get_media_metadata, format_metadata_for_display
from py_home_gallery.utils.security import get_safe_path
from py_home_gallery.utils.logger import get_logger
import os
import json
import random

bp = Blueprint('metadata', __name__)
logger = get_logger(__name__)


@bp.route('/api/metadata/<path:media_path>')
def get_metadata(media_path):
    """
    Get metadata for a specific media file.

    Args:
        media_path: Relative path to the media file

    Returns:
        JSON response with metadata
    """
    media_root = current_app.config['MEDIA_ROOT']

    # Security check: ensure path is safe and get full path
    full_path = get_safe_path(media_root, media_path)

    if not full_path:
        return jsonify({'error': 'Invalid file path'}), 403

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Get raw metadata
        metadata = get_media_metadata(full_path)

        # Format for display
        formatted = format_metadata_for_display(metadata)

        # Test JSON serialization of formatted data
        try:
            json.dumps(formatted)
        except (TypeError, ValueError) as e:
            print(f"Error: Formatted metadata not JSON serializable for {media_path}: {e}")
            print(f"Formatted data: {formatted}")
            # Try to clean the formatted data
            import copy
            cleaned = {}
            for section, data in formatted.items():
                cleaned[section] = {}
                if isinstance(data, dict):
                    for k, v in data.items():
                        try:
                            json.dumps({k: v})
                            cleaned[section][k] = v
                        except:
                            print(f"  Skipping {section}.{k} = {v} (type: {type(v)})")
                            cleaned[section][k] = str(v)
            formatted = cleaned

        # Test JSON serialization of raw metadata
        try:
            json.dumps(metadata)
            include_raw = True
        except (TypeError, ValueError) as e:
            print(f"Warning: Raw metadata not JSON serializable for {media_path}: {e}")
            include_raw = False

        response_data = {
            'success': True,
            'path': media_path,
            'metadata': formatted
        }

        if include_raw:
            response_data['raw'] = metadata

        # Create response with sort_keys=False to avoid int/str comparison errors
        response = make_response(json.dumps(response_data, sort_keys=False))
        response.headers['Content-Type'] = 'application/json'
        return response

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Metadata error for {media_path}:")
        print(error_trace)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/mosaic')
def mosaic():
    """
    Get random thumbnails for mosaic display.

    Query Parameters:
        count (int): Number of thumbnails to return (default: 100, max: 500)

    Returns:
        JSON response with list of thumbnail paths

    Example:
        /api/mosaic?count=50
        /api/mosaic?count=200
    """
    thumbnail_dir = current_app.config['THUMBNAIL_DIR']

    # Get count from query parameter (default 100, max 500)
    try:
        requested_count = int(request.args.get('count', 100))
        requested_count = max(1, min(requested_count, 500))  # Clamp between 1 and 500
    except ValueError:
        requested_count = 100

    try:
        # Get all thumbnail files
        thumbnails = []
        for root, dirs, files in os.walk(thumbnail_dir):
            for file in files:
                # Only include image files
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    # Get relative path from thumbnail dir
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, thumbnail_dir)
                    # Convert to URL-safe path (forward slashes, not backslashes)
                    url_path = rel_path.replace('\\', '/')
                    # Return as mosaic thumbnail URL (direct serving, no generation)
                    thumbnails.append(f'/mosaic-thumb/{url_path}')

        logger.info(f"Found {len(thumbnails)} total thumbnails, requested {requested_count}")

        # Pick random thumbnails (requested count or all if less available)
        count = min(requested_count, len(thumbnails))
        random_thumbnails = random.sample(thumbnails, count) if thumbnails else []

        return jsonify({
            'success': True,
            'thumbnails': random_thumbnails,
            'count': count,
            'requested': requested_count,
            'total': len(thumbnails)
        })

    except Exception as e:
        logger.error(f"Error generating mosaic: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
