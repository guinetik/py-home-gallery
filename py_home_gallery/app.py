"""
Flask application setup module for Py Home Gallery.

This module creates and configures the Flask application,
registering routes and setting up the application context.
"""

from flask import Flask
from py_home_gallery.routes import register_routes


def create_app(config):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="../templates")
    
    # Store configuration in app config
    app.config['MEDIA_ROOT'] = config.media_dir
    app.config['THUMBNAIL_DIR'] = config.thumbnail_dir
    app.config['ITEMS_PER_PAGE'] = config.items_per_page
    app.config['PLACEHOLDER_URL'] = config.placeholder_url
    
    # Register all route blueprints
    register_routes(app)
    
    return app
