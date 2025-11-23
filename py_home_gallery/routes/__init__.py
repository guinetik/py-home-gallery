"""
Routes subpackage for Py Home Gallery.

This package contains Flask route definitions for:
- Gallery views
- Media serving
- Infinite scrolling
- Metadata API
"""

from py_home_gallery.routes import gallery, media, infinite, metadata, browse

# Redefine the register_routes function to use our blueprint modules
def register_routes(app):
    """
    Register all route blueprints with the Flask application.

    Media routes are always registered as fallback for Nginx (on-demand thumbnail generation).
    When SERVE_MEDIA is False, Nginx serves existing files first, Flask generates missing ones.
    """
    app.register_blueprint(gallery.bp)
    app.register_blueprint(browse.bp)
    app.register_blueprint(infinite.bp)
    app.register_blueprint(metadata.bp)
    app.register_blueprint(media.bp)  # Always register for fallback

    # Just informational message
    if app.config.get('SERVE_MEDIA', True):
        print("✓ Flask serving all media files directly")
    else:
        print("✓ Nginx serving media (Flask fallback for missing thumbnails)")
