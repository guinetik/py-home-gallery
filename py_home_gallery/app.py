"""
Flask application setup module for Py Home Gallery.

This module creates and configures the Flask application,
registering routes and setting up the application context.
"""

from flask import Flask
from py_home_gallery.routes import register_routes
import os


def create_app(config):
    """Create and configure the Flask application."""
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
    
    # Register all route blueprints
    register_routes(app)
    
    # Print static folder information for debugging
    print(f"Static folder configured at: {static_folder_path}")
    print(f"Static URL path: /static")
    
    return app
