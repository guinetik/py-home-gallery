"""
Application-wide constants for Py Home Gallery.

This module centralizes all magic numbers and configuration constants
to make the codebase more maintainable and easier to understand.
"""

# ============================================================================
# PAGINATION & DISPLAY
# ============================================================================

# Default number of items per page in gallery views
DEFAULT_ITEMS_PER_PAGE = 50

# Maximum number of items to show in random gallery (no pagination)
RANDOM_GALLERY_MAX_ITEMS = 100

# Number of random thumbnails to show in mosaic background
MOSAIC_DEFAULT_COUNT = 100
MOSAIC_MAX_COUNT = 500
MOSAIC_MIN_COUNT = 1


# ============================================================================
# THUMBNAILS
# ============================================================================

# Default thumbnail dimensions
THUMBNAIL_WIDTH = 300
THUMBNAIL_HEIGHT = 200

# Thumbnail aspect ratio (16:9 for videos)
THUMBNAIL_ASPECT_WIDTH = 16
THUMBNAIL_ASPECT_HEIGHT = 9

# Computed 16:9 thumbnail dimensions
THUMBNAIL_169_WIDTH = 300
THUMBNAIL_169_HEIGHT = 169  # 300 * 9 / 16

# Media dimension validation bounds
MIN_MEDIA_DIMENSION = 10
MAX_MEDIA_DIMENSION = 50000


# ============================================================================
# CACHING
# ============================================================================

# Default cache TTL (Time To Live) in seconds
DEFAULT_CACHE_TTL = 300  # 5 minutes

# Metadata cache lives 2x longer than directory cache
METADATA_CACHE_MULTIPLIER = 2

# Cache key prefixes
CACHE_PREFIX_DIRECTORY = "dir:"
CACHE_PREFIX_FILE = "file:"
CACHE_SUFFIX_WITH_DIMS = "_with_dims"
CACHE_SUFFIX_NO_DIMS = "_no_dims"


# ============================================================================
# BACKGROUND WORKERS
# ============================================================================

# Default number of thumbnail generation worker threads
DEFAULT_WORKER_THREADS = 2

# Maximum queue size for thumbnail generation jobs
WORKER_MAX_QUEUE_SIZE = 500

# Batch size for preloading thumbnails
PRELOAD_BATCH_SIZE = 500

# Worker job timeout in seconds
WORKER_JOB_TIMEOUT = 30.0


# ============================================================================
# SERVER
# ============================================================================

# Default host (0.0.0.0 means all interfaces)
DEFAULT_HOST = "0.0.0.0"

# Default port
DEFAULT_PORT = 8000

# Production server thread count
PRODUCTION_SERVER_THREADS = 4


# ============================================================================
# PLACEHOLDER
# ============================================================================

# Default placeholder image URL
DEFAULT_PLACEHOLDER_URL = "https://via.placeholder.com/300x200"


# ============================================================================
# FILE TYPES
# ============================================================================

# Supported image extensions
IMAGE_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'
)

# Supported video extensions
VIDEO_EXTENSIONS = (
    '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'
)

# All supported media extensions
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS

# Default dimensions for different media types (when not extracting)
DEFAULT_VIDEO_WIDTH = 1920
DEFAULT_VIDEO_HEIGHT = 1080
DEFAULT_IMAGE_WIDTH = 1600
DEFAULT_IMAGE_HEIGHT = 1200


# ============================================================================
# PATHS
# ============================================================================

# Default media directory (relative to run location)
DEFAULT_MEDIA_DIR = "./media"

# Default thumbnail directory name (inside user home)
THUMBNAIL_DIR_NAME = ".py-home-gallery"
THUMBNAIL_SUBDIR_NAME = "thumbnails"

# Default log directory
DEFAULT_LOG_DIR = "./logs"
DEFAULT_LOG_FILENAME = "app.log"


# ============================================================================
# SECURITY
# ============================================================================

# Dangerous characters for filename sanitization
DANGEROUS_FILENAME_CHARS = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*', '\0']
