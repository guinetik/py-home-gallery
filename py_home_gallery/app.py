"""
Flask application setup module for Py Home Gallery.

This module creates and configures the Flask application,
registering routes and setting up the application context.
"""

from flask import Flask
from py_home_gallery.routes import register_routes
from py_home_gallery.workers.thumbnail_worker import shutdown_thumbnail_worker
from py_home_gallery.workers.preload import preload_all
from py_home_gallery.utils.cache import setup_caches
from py_home_gallery.utils.logger import configure_logging
from py_home_gallery.constants import METADATA_CACHE_MULTIPLIER
import os
import atexit


def create_app(config):
    """Create and configure the Flask application."""
    # Configure logging first (before any other imports that use logger)
    configure_logging(
        log_level=config.log_level,
        log_to_file=config.log_to_file,
        log_dir=config.log_dir
    )
    # Set up static folder path at project root level
    static_folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    # Create Flask app with both template and static folder paths
    app = Flask(__name__, 
                template_folder="../templates",
                static_folder=static_folder_path,
                static_url_path='/static')
    
    # Store configuration in app config
    app.config['MEDIA_ROOT'] = config.media_dir
    app.config['THUMBNAIL_DIR'] = config.thumbnail_dir
    app.config['ITEMS_PER_PAGE'] = config.items_per_page
    app.config['PLACEHOLDER_URL'] = config.placeholder_url
    app.config['SERVE_MEDIA'] = config.serve_media
    app.config['CACHE_ENABLED'] = config.cache_enabled
    app.config['CACHE_TTL'] = config.cache_ttl
    app.config['WORKER_ENABLED'] = config.worker_enabled
    app.config['WORKER_THREADS'] = config.worker_threads
    
    # Initialize cache with config TTL (metadata cache gets 2x TTL by default)
    if config.cache_enabled:
        setup_caches(
            directory_ttl=config.cache_ttl,
            metadata_ttl=config.cache_ttl * METADATA_CACHE_MULTIPLIER
        )
    
    # Register all route blueprints
    register_routes(app)
    
    # Register cleanup handler for worker shutdown
    atexit.register(shutdown_thumbnail_worker)

    # Preload cache if enabled (independent of workers)
    if config.cache_enabled:
        from py_home_gallery.media.scanner import scan_directory
        from py_home_gallery.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Warming up directory cache...")
        try:
            # Scan without dimensions for faster startup, dimensions added per-page later
            files = scan_directory(config.media_dir, use_cache=True, include_dimensions=False)
            logger.info(f"✓ Cache warmed: {len(files)} files indexed")
        except Exception as e:
            logger.error(f"Error warming cache: {e}")

    # Preload thumbnails in background if workers enabled
    if config.worker_enabled:
        from py_home_gallery.workers.preload import preload_thumbnails
        preload_thumbnails(
            media_root=config.media_dir,
            thumbnail_dir=config.thumbnail_dir,
            num_threads=config.worker_threads
        )
    
    # Log configuration
    logger = get_logger(__name__)
    logger.info(f"Static folder configured at: {static_folder_path}")
    logger.info(f"Static URL path: /static")
    logger.info(f"Cache: {'Enabled' if config.cache_enabled else 'Disabled'}")
    logger.info(f"Background Workers: {config.worker_threads if config.worker_enabled else 'Disabled'}")

    return app
