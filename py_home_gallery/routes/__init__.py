"""
Routes subpackage for Py Home Gallery.

This package contains Flask route definitions for:
- Gallery views
- Media serving
- Infinite scrolling
"""

from py_home_gallery.routes import gallery, media, infinite

# Redefine the register_routes function to use our blueprint modules
def register_routes(app):
    """
    Register all route blueprints with the Flask application.
    """
    app.register_blueprint(gallery.bp)
    app.register_blueprint(media.bp)
    app.register_blueprint(infinite.bp)
