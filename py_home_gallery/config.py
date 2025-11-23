"""
Configuration handling module for Py Home Gallery.

This module handles command-line arguments, environment variables,
and application configuration settings.
"""

import os
import sys
from argparse import ArgumentParser
from py_home_gallery.constants import (
    DEFAULT_ITEMS_PER_PAGE,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PLACEHOLDER_URL,
    DEFAULT_CACHE_TTL,
    DEFAULT_WORKER_THREADS,
    DEFAULT_MEDIA_DIR,
    THUMBNAIL_DIR_NAME,
    THUMBNAIL_SUBDIR_NAME,
    DEFAULT_LOG_DIR,
)


class Config:
    """Application configuration loaded from command-line args and environment variables."""
    
    def __init__(self):
        """Initialize default configuration values."""
        default_thumb_dir = os.path.join(
            os.path.expanduser('~'),
            THUMBNAIL_DIR_NAME,
            THUMBNAIL_SUBDIR_NAME
        )

        self.media_dir = os.environ.get('PY_HOME_GALLERY_MEDIA_DIR', DEFAULT_MEDIA_DIR)
        self.thumbnail_dir = os.environ.get('PY_HOME_GALLERY_THUMB_DIR', default_thumb_dir)
        self.items_per_page = int(os.environ.get('PY_HOME_GALLERY_ITEMS_PER_PAGE', str(DEFAULT_ITEMS_PER_PAGE)))
        self.host = os.environ.get('PY_HOME_GALLERY_HOST', DEFAULT_HOST)
        self.port = int(os.environ.get('PY_HOME_GALLERY_PORT') or os.environ.get('PORT', str(DEFAULT_PORT)))
        self.placeholder_url = os.environ.get('PY_HOME_GALLERY_PLACEHOLDER', DEFAULT_PLACEHOLDER_URL)
        self.skip_ffmpeg_check = False

        # Cache settings
        self.cache_enabled = os.environ.get('PY_HOME_GALLERY_CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_ttl = int(os.environ.get('PY_HOME_GALLERY_CACHE_TTL', str(DEFAULT_CACHE_TTL)))

        # Worker settings
        self.worker_threads = int(os.environ.get('PY_HOME_GALLERY_WORKER_THREADS', str(DEFAULT_WORKER_THREADS)))
        self.worker_enabled = os.environ.get('PY_HOME_GALLERY_WORKER_ENABLED', 'true').lower() == 'true'

        # Media serving settings
        self.serve_media = os.environ.get('PY_HOME_GALLERY_SERVE_MEDIA', 'true').lower() == 'true'

        # Production mode settings
        self.production = os.environ.get('PY_HOME_GALLERY_PRODUCTION', 'false').lower() == 'true'

        # Logging settings
        self.log_level = os.environ.get('PY_HOME_GALLERY_LOG_LEVEL', 'INFO').upper()
        self.log_to_file = os.environ.get('PY_HOME_GALLERY_LOG_TO_FILE', 'true').lower() == 'true'
        self.log_dir = os.environ.get('PY_HOME_GALLERY_LOG_DIR', DEFAULT_LOG_DIR)
        
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
        
        # Cache and worker settings
        self.cache_ttl = parsed_args.cache_ttl
        self.worker_threads = parsed_args.worker_threads
        self.cache_enabled = not parsed_args.no_cache
        self.worker_enabled = not parsed_args.no_worker

        # Media serving settings (only override if flag was explicitly passed)
        if parsed_args.no_serve_media:
            self.serve_media = False
        # else: keep env var value

        # Production mode settings (only override if flag was explicitly passed)
        if parsed_args.production:
            self.production = True
        # else: keep env var value

        # Logging settings
        self.log_level = parsed_args.log_level
        self.log_to_file = not parsed_args.no_log_file
        self.log_dir = parsed_args.log_dir
        
        return self
    
    def _create_arg_parser(self):
        """Create argument parser with application options."""
        parser = ArgumentParser(description='Media Gallery Server')
        
        parser.add_argument(
            '--media-dir',
            type=str,
            default=self.media_dir,
            help=f'Root directory containing media files (default: {DEFAULT_MEDIA_DIR}). '
                 'ENV: PY_HOME_GALLERY_MEDIA_DIR (CMD: %%USERPROFILE%%\\Media, PowerShell: $env:USERPROFILE\\Media)'
        )

        parser.add_argument(
            '--thumbnail-dir',
            type=str,
            default=self.thumbnail_dir,
            help=f'Directory to store generated thumbnails '
                 f'(default: ~/{THUMBNAIL_DIR_NAME}/{THUMBNAIL_SUBDIR_NAME} on Linux/Mac or C:\\Users\\YourUsername\\{THUMBNAIL_DIR_NAME}\\{THUMBNAIL_SUBDIR_NAME} on Windows). '
                 'ENV: PY_HOME_GALLERY_THUMB_DIR'
        )

        parser.add_argument(
            '--items-per-page',
            type=int,
            default=self.items_per_page,
            help=f'Number of items to display per page (default: {DEFAULT_ITEMS_PER_PAGE}). '
                 'ENV: PY_HOME_GALLERY_ITEMS_PER_PAGE'
        )

        parser.add_argument(
            '--host',
            type=str,
            default=self.host,
            help=f'Host to run the server on (default: {DEFAULT_HOST}). '
                 'ENV: PY_HOME_GALLERY_HOST'
        )

        parser.add_argument(
            '--port',
            type=int,
            default=self.port,
            help=f'Port to run the server on (default: {DEFAULT_PORT}). '
                 'ENV: PY_HOME_GALLERY_PORT'
        )

        parser.add_argument(
            '--placeholder',
            type=str,
            default=self.placeholder_url,
            help=f'URL for placeholder thumbnails (default: {DEFAULT_PLACEHOLDER_URL}). '
                 'ENV: PY_HOME_GALLERY_PLACEHOLDER'
        )
        
        parser.add_argument(
            '--skip-ffmpeg-check',
            action='store_true',
            help='Skip the check for FFmpeg installation (use at your own risk)'
        )
        
        parser.add_argument(
            '--cache-ttl',
            type=int,
            default=self.cache_ttl,
            help=f'Cache TTL in seconds (default: {DEFAULT_CACHE_TTL}). '
                 'ENV: PY_HOME_GALLERY_CACHE_TTL'
        )

        parser.add_argument(
            '--worker-threads',
            type=int,
            default=self.worker_threads,
            help=f'Number of background worker threads (default: {DEFAULT_WORKER_THREADS}). '
                 'ENV: PY_HOME_GALLERY_WORKER_THREADS'
        )
        
        parser.add_argument(
            '--no-cache',
            action='store_true',
            help='Disable caching'
        )
        
        parser.add_argument(
            '--no-worker',
            action='store_true',
            help='Disable background thumbnail generation'
        )

        parser.add_argument(
            '--no-serve-media',
            action='store_true',
            help='Disable Flask media file serving (for use with external server like Nginx). '
                 'ENV: PY_HOME_GALLERY_SERVE_MEDIA'
        )

        parser.add_argument(
            '--production',
            action='store_true',
            help='Run in production mode using Waitress WSGI server (requires: pip install waitress). '
                 'ENV: PY_HOME_GALLERY_PRODUCTION'
        )

        parser.add_argument(
            '--log-level',
            type=str,
            default=self.log_level,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Logging level (default: INFO). '
                 'ENV: PY_HOME_GALLERY_LOG_LEVEL'
        )
        
        parser.add_argument(
            '--no-log-file',
            action='store_true',
            help='Disable logging to file (log to console only)'
        )
        
        parser.add_argument(
            '--log-dir',
            type=str,
            default=self.log_dir,
            help='Directory for log files (default: ./logs). '
                 'ENV: PY_HOME_GALLERY_LOG_DIR'
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
        
        # Create log directory if logging to file is enabled
        if self.log_to_file:
            os.makedirs(self.log_dir, exist_ok=True)
        
        return self
        
    def display(self):
        """Display the current configuration."""
        print(f"Media Gallery Server Configuration:")
        print(f"Media Directory: {self.media_dir}")
        print(f"Thumbnail Directory: {self.thumbnail_dir}")
        print(f"Items Per Page: {self.items_per_page}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Production Mode: {self.production}")
        print(f"Serve Media: {self.serve_media}")
        print(f"Cache Enabled: {self.cache_enabled} (TTL: {self.cache_ttl}s)")
        print(f"Background Workers: {self.worker_threads if self.worker_enabled else 'Disabled'}")
        print(f"Log Level: {self.log_level}")
        print(f"Log to File: {self.log_to_file}{f' (Dir: {self.log_dir})' if self.log_to_file else ''}")


def load_config():
    """Load and return application configuration from all sources."""
    return Config().load_from_args().validate()
