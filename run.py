"""
Entry point script for Py Home Gallery.

This script is the main entry point for running the Py Home Gallery application.
It handles configuration loading, validation, and application startup.
"""

import sys
from py_home_gallery.config import load_config
from py_home_gallery.utils.ffmpeg import check_ffmpeg
from py_home_gallery.app import create_app


def main():
    """Main entry point for the application."""
    # Load configuration
    config = load_config()
    
    # Check for FFmpeg installation if not skipped
    if not config.skip_ffmpeg_check and not check_ffmpeg():
        print("Error: FFmpeg not found in PATH. FFmpeg is required for video thumbnail generation.")
        print("Please install FFmpeg and make sure it's accessible in your PATH, or use --skip-ffmpeg-check to bypass this check.")
        sys.exit(1)
    
    # Display configuration
    config.display()
    
    # Create the application
    app = create_app(config)

    # Run in production or development mode
    if config.production:
        # Production mode: Use Waitress WSGI server
        try:
            from waitress import serve
            print(f"\n{'='*60}")
            print(f"🚀 Starting production server with Waitress")
            print(f"{'='*60}")
            print(f"Server running at: http://{config.host}:{config.port}")
            print(f"Press CTRL+C to stop\n")
            serve(app, host=config.host, port=config.port, threads=4)
        except ImportError:
            print("\n❌ ERROR: Waitress is not installed!")
            print("Production mode requires Waitress WSGI server.")
            print("\nInstall it with:")
            print("  pip install waitress")
            print("\nOr run without --production flag to use Flask development server.")
            sys.exit(1)
    else:
        # Development mode: Use Flask built-in server with threading
        print(f"\n{'='*60}")
        print(f"⚠️  Development server (not for production!)")
        print(f"{'='*60}")
        print(f"Use --production flag for production deployment\n")
        app.run(host=config.host, port=config.port, threaded=True)


if __name__ == '__main__':
    main()
