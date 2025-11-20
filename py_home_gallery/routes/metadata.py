"""
Metadata API routes for Py Home Gallery.

This module provides API endpoints for retrieving media metadata.
"""

from flask import Blueprint, jsonify, current_app, make_response
from py_home_gallery.utils.metadata import get_media_metadata, format_metadata_for_display
from py_home_gallery.utils.security import get_safe_path
import os
import json

bp = Blueprint('metadata', __name__)


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
