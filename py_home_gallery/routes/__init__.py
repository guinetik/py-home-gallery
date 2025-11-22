"""
Routes subpackage for Py Home Gallery.

This package contains Flask route definitions for:
- Gallery views
- Media serving
- Infinite scrolling
- Metadata API
"""

from py_home_gallery.routes import gallery, media, infinite, metadata

# Redefine the register_routes function to use our blueprint modules
def register_routes(app):
    """
    Register all route blueprints with the Flask application.

    If SERVE_MEDIA is False, the media blueprint will not be registered,
    allowing an external server (like Nginx) to serve media files.
    """
    app.register_blueprint(gallery.bp)
    app.register_blueprint(infinite.bp)
    app.register_blueprint(metadata.bp)

    # Conditionally register media serving routes
    if app.config.get('SERVE_MEDIA', True):
        app.register_blueprint(media.bp)
        print("✓ Flask serving media files (use --no-serve-media to disable)")
    else:
        print("✓ Media serving disabled - expecting external server (Nginx/etc.)")
