"""
Media serving routes for Py Home Gallery.

This module contains route handlers for serving media files,
including original media and thumbnails.
"""

import os
from flask import Blueprint, send_file, current_app, abort
from py_home_gallery.media.thumbnails import ensure_thumbnail_exists
from py_home_gallery.utils.security import get_safe_path, validate_media_extension
from py_home_gallery.utils.logger import get_logger
from py_home_gallery.workers.thumbnail_worker import get_thumbnail_worker

logger = get_logger(__name__)

# Create a blueprint for media routes
bp = Blueprint('media', __name__)

# Get the global thumbnail worker
thumbnail_worker = get_thumbnail_worker(num_threads=2)


@bp.route('/thumbnail/<path:filename>')
def serve_thumbnail(filename):
    """
    Serve generated thumbnails for videos, creating them on-demand or in background.
    
    Security: Validates path to prevent traversal attacks.
    Performance: Uses background worker for thumbnail generation.
    """
    media_root = current_app.config['MEDIA_ROOT']
    thumbnail_dir = current_app.config['THUMBNAIL_DIR']
    placeholder_url = current_app.config['PLACEHOLDER_URL']
    
    try:
        # Validate the filename for security
        if not validate_media_extension(filename):
            logger.warning(f"Invalid file extension requested for thumbnail: {filename}")
            abort(400, description="Invalid file type")
        
        # Validate path traversal protection
        media_file_path = get_safe_path(media_root, filename)
        if not media_file_path:
            logger.warning(f"Path traversal attempt in thumbnail request: {filename}")
            abort(403, description="Access denied")
        
        # Check if thumbnail already exists
        safe_filename = filename.replace('\\', '_').replace('/', '_')
        if len(safe_filename) > 200:
            import hashlib
            file_hash = hashlib.md5(safe_filename.encode()).hexdigest()
            extension = os.path.splitext(safe_filename)[1]
            safe_filename = f"{file_hash}{extension}"
        
        thumbnail_path = os.path.join(thumbnail_dir, f"{safe_filename}.png")
        
        # If thumbnail exists and is valid, serve it immediately
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            logger.debug(f"Serving existing thumbnail: {filename}")
            return send_file(thumbnail_path)

        # Thumbnail doesn't exist - generate it synchronously (blocking request)
        logger.info(f"Thumbnail not found, generating synchronously: {filename}")

        # Ensure media file exists
        if not media_file_path or not os.path.exists(media_file_path):
            logger.warning(f"Media file not found for thumbnail: {filename}")
            abort(404, description="Media file not found")

        # Generate thumbnail synchronously - this will block until done
        thumbnail_result = ensure_thumbnail_exists(
            media_root,
            thumbnail_dir,
            filename,
            placeholder_url
        )

        # Check if generation was successful
        if thumbnail_result and thumbnail_result != placeholder_url:
            if os.path.exists(thumbnail_result) and os.path.getsize(thumbnail_result) > 0:
                logger.info(f"Successfully generated thumbnail: {filename}")
                return send_file(thumbnail_result)

        # Generation failed - return 404
        logger.error(f"Failed to generate thumbnail for: {filename}")
        abort(404, description="Thumbnail generation failed")
    
    except Exception as e:
        logger.error(f"Error serving thumbnail for {filename}: {e}")
        return placeholder_url or abort(500, description="Internal server error")


@bp.route('/media/<path:filename>')
def serve_media(filename):
    """
    Serve media files with path traversal protection.
    
    Security: Validates path to prevent traversal attacks and only serves allowed file types.
    """
    media_root = current_app.config['MEDIA_ROOT']
    
    try:
        logger.debug(f"Attempting to serve media file: {filename}")
        
        # Validate file extension
        if not validate_media_extension(filename):
            logger.warning(f"Invalid file extension requested: {filename}")
            abort(400, description="Invalid file type")
        
        # Use safe path validation to prevent path traversal
        file_path = get_safe_path(media_root, filename)
        
        if not file_path:
            logger.warning(f"Path traversal attempt detected: {filename}")
            abort(403, description="Access denied")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            
            # Try to find the file in subdirectories (fallback for legacy paths)
            basename = os.path.basename(filename)
            logger.debug(f"Searching for file by basename: {basename}")
            
            try:
                for root, _, files in os.walk(media_root):
                    if basename in files:
                        candidate_path = os.path.join(root, basename)
                        
                        # Validate the found path is also safe
                        rel_path = os.path.relpath(candidate_path, media_root)
                        safe_candidate = get_safe_path(media_root, rel_path)
                        
                        if safe_candidate and os.path.exists(safe_candidate):
                            logger.info(f"Found file at alternative location: {safe_candidate}")
                            return send_file(safe_candidate)
            except Exception as e:
                logger.error(f"Error during file search: {e}")
            
            # If we get here, no matching file was found
            abort(404, description=f"File not found: {filename}")
        
        # Check file permissions
        if not os.access(file_path, os.R_OK):
            logger.error(f"Permission denied reading file: {file_path}")
            abort(403, description="Permission denied")
        
        logger.info(f"Serving media file: {filename}")
        return send_file(file_path)
    
    except Exception as e:
        logger.error(f"Error serving media file {filename}: {e}")
        abort(500, description="Internal server error")
