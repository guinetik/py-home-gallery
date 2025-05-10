"""
Configuration handling module for Py Home Gallery.

This module handles command-line arguments, environment variables,
and application configuration settings.
"""

import os
import sys
from argparse import ArgumentParser


class Config:
    """Application configuration loaded from command-line args and environment variables."""
    
    def __init__(self):
        """Initialize default configuration values."""
        self.media_dir = os.environ.get('PY_HOME_GALLERY_MEDIA_DIR', './media')
        self.thumbnail_dir = os.path.join(os.path.expanduser('~'), '.py-home-gallery', 'thumbnails')
        self.thumbnail_dir = os.environ.get('PY_HOME_GALLERY_THUMB_DIR', self.thumbnail_dir)
        self.items_per_page = int(os.environ.get('PY_HOME_GALLERY_ITEMS_PER_PAGE', '50'))
        self.host = os.environ.get('PY_HOME_GALLERY_HOST', '0.0.0.0')
        self.port = int(os.environ.get('PY_HOME_GALLERY_PORT') or os.environ.get('PORT', '8000'))
        self.placeholder_url = os.environ.get('PY_HOME_GALLERY_PLACEHOLDER', 'https://via.placeholder.com/300x200')
        self.skip_ffmpeg_check = False
        
    def load_from_args(self, args=None):
        """Load configuration from command-line arguments."""
        parser = self._create_arg_parser()
        parsed_args = parser.parse_args(args)
        
        self.media_dir = parsed_args.media_dir
        self.thumbnail_dir = parsed_args.thumbnail_dir
        self.items_per_page = parsed_args.items_per_page
        self.host = parsed_args.host
        self.port = parsed_args.port
        self.placeholder_url = parsed_args.placeholder
        self.skip_ffmpeg_check = parsed_args.skip_ffmpeg_check
        
        return self
    
    def _create_arg_parser(self):
        """Create argument parser with application options."""
        parser = ArgumentParser(description='Media Gallery Server')
        
        parser.add_argument(
            '--media-dir', 
            type=str, 
            default=self.media_dir,
            help='Root directory containing media files (default: ./media). '
                 'ENV: PY_HOME_GALLERY_MEDIA_DIR (CMD: %%USERPROFILE%%\\Media, PowerShell: $env:USERPROFILE\\Media)'
        )
        
        parser.add_argument(
            '--thumbnail-dir', 
            type=str, 
            default=self.thumbnail_dir,
            help='Directory to store generated thumbnails '
                 '(default: ~/.py-home-gallery/thumbnails on Linux/Mac or C:\\Users\\YourUsername\\.py-home-gallery\\thumbnails on Windows). '
                 'ENV: PY_HOME_GALLERY_THUMB_DIR'
        )
        
        parser.add_argument(
            '--items-per-page', 
            type=int, 
            default=self.items_per_page,
            help='Number of items to display per page (default: 50). '
                 'ENV: PY_HOME_GALLERY_ITEMS_PER_PAGE'
        )
        
        parser.add_argument(
            '--host', 
            type=str, 
            default=self.host,
            help='Host to run the server on (default: 0.0.0.0). '
                 'ENV: PY_HOME_GALLERY_HOST'
        )
        
        parser.add_argument(
            '--port', 
            type=int, 
            default=self.port,
            help='Port to run the server on (default: 8000). '
                 'ENV: PY_HOME_GALLERY_PORT'
        )
        
        parser.add_argument(
            '--placeholder', 
            type=str, 
            default=self.placeholder_url,
            help='URL for placeholder thumbnails (default: https://via.placeholder.com/300x200). '
                 'ENV: PY_HOME_GALLERY_PLACEHOLDER'
        )
        
        parser.add_argument(
            '--skip-ffmpeg-check',
            action='store_true',
            help='Skip the check for FFmpeg installation (use at your own risk)'
        )
        
        return parser
        
    def validate(self):
        """Validate the configuration."""
        self.media_dir = os.path.abspath(self.media_dir)
        self.thumbnail_dir = os.path.abspath(self.thumbnail_dir)
        
        if not os.path.exists(self.media_dir):
            print(f"Error: Media directory '{self.media_dir}' does not exist.")
            sys.exit(1)
            
        if not os.path.isdir(self.media_dir):
            print(f"Error: Media path '{self.media_dir}' is not a directory.")
            sys.exit(1)
            
        # Create thumbnail directory if it doesn't exist
        os.makedirs(self.thumbnail_dir, exist_ok=True)
        
        return self
        
    def display(self):
        """Display the current configuration."""
        print(f"Media Gallery Server Configuration:")
        print(f"Media Directory: {self.media_dir}")
        print(f"Thumbnail Directory: {self.thumbnail_dir}")
        print(f"Items Per Page: {self.items_per_page}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")


def load_config():
    """Load and return application configuration from all sources."""
    return Config().load_from_args().validate()
