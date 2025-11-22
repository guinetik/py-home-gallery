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
    
    # Create and run the application
    app = create_app(config)
    app.run(host=config.host, port=config.port, threaded=True)


if __name__ == '__main__':
    main()
