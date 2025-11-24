# Architecture - Py Home Gallery

## Overview

Py Home Gallery follows a modular Flask application architecture with clear separation of concerns. The application is organized into distinct layers: routes, business logic, utilities, and background workers.

## Project Structure

```
py-home-gallery/
├── py_home_gallery/              # Main package
│   ├── __init__.py
│   ├── app.py                    # Flask application factory
│   ├── config.py                 # Configuration management
│   │
│   ├── media/                    # Media handling module
│   │   ├── __init__.py
│   │   ├── scanner.py           # Directory scanning
│   │   ├── thumbnails.py        # Thumbnail generation
│   │   ├── utils.py             # Media utilities
│   │   ├── dimensions.py        # Media dimension extraction
│   │   └── dimension_helper.py  # Dimension helper functions
│   │
│   ├── routes/                   # Flask route blueprints
│   │   ├── __init__.py
│   │   ├── gallery.py           # Gallery routes (/, /gallery, /random, /new)
│   │   ├── browse.py            # Browse routes (/browse, /api/browse)
│   │   ├── infinite.py          # Infinite scroll routes (/infinite, /gallery-data)
│   │   ├── media.py             # Media serving routes (/media, /thumbnail, /mosaic-thumb)
│   │   └── metadata.py          # Metadata API routes (/api/metadata, /api/mosaic)
│   │
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   ├── cache.py             # Caching system
│   │   ├── logger.py            # Logging system
│   │   ├── security.py          # Security utilities
│   │   ├── pagination.py        # Pagination utilities
│   │   ├── metadata.py          # Metadata extraction
│   │   └── ffmpeg.py            # FFmpeg validation
│   │
│   ├── constants.py             # Application-wide constants
│   │
│   └── workers/                  # Background workers
│       ├── __init__.py
│       ├── thumbnail_worker.py  # Thumbnail generation worker
│       └── preload.py           # Cache preloading
│
├── templates/                    # Jinja2 templates
│   ├── index.html               # Home page
│   ├── browse.html              # Browse page (3D Cover Flow)
│   ├── gallery.html             # Gallery view
│   └── infinite.html            # Infinite scroll view
│
├── static/                       # Static assets
│   ├── style.css                # Stylesheet
│   ├── gallery.js               # Gallery JavaScript
│   ├── metadata.js              # Metadata JavaScript
│   ├── theme.js                 # Theme system
│   └── logo.svg                 # Logo
│
├── docs/                         # Documentation
├── logs/                         # Log files
├── samplegallery/               # Sample media for testing
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
└── nginx.conf                   # Nginx configuration
```

## Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER INTERFACE                    │
│  (Browser - Templates HTML + CSS + JavaScript)      │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│                   ROUTES LAYER                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐    │
│  │ gallery  │ │  browse  │ │ infinite │ │media │    │
│  │  routes  │ │  routes  │ │  routes  │ │routes│    │
│  └──────────┘ └──────────┘ └──────────┘ └──────┘    │
│  ┌──────────┐                                       │
│  │metadata  │                                       │
│  │  routes  │                                       │
│  └──────────┘                                       │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│                 BUSINESS LOGIC                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │
│  │   scanner    │  │  thumbnails  │  │   utils  │   │
│  │              │  │              │  │          │   │
│  └──────────────┘  └──────────────┘  └──────────┘   │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  dimensions  │  │  metadata    │                 │
│  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│              CROSS-CUTTING CONCERNS                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │
│  │   security   │  │   logger     │  │   cache  │   │
│  │              │  │              │  │          │   │
│  └──────────────┘  └──────────────┘  └──────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │
│  │  pagination  │  │   config     │  │constants │   │
│  └──────────────┘  └──────────────┘  └──────────┘   │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│              BACKGROUND WORKERS                     │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  thumbnail   │  │   preload    │                 │
│  │    worker    │  │              │                 │
│  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│                 FILESYSTEM LAYER                    │
│        (Media Files, Thumbnails, Logs)              │
└─────────────────────────────────────────────────────┘
```

## Module Responsibilities

### Routes Layer (`py_home_gallery/routes/`)

**gallery.py** - Main gallery views
- `/` - Home page with mosaic background
- `/gallery` - Standard gallery view with pagination
- `/random` - Randomized gallery view
- `/new` - Gallery sorted by newest files first
- `/api/stats` - Statistics API endpoint

**browse.py** - Folder browsing
- `/browse` - 3D Cover Flow browse page
- `/api/browse` - Browse API endpoint (returns folders with thumbnails)

**infinite.py** - Infinite scroll view
- `/infinite` - Infinite scroll gallery page
- `/gallery-data` - Paginated data endpoint for infinite scroll

**media.py** - Media file serving
- `/media/<path>` - Serve media files
- `/thumbnail/<path>` - Serve or generate thumbnails
- `/mosaic-thumb/<path>` - Serve mosaic thumbnails

**metadata.py** - Metadata API
- `/api/metadata/<path>` - Get media file metadata
- `/api/mosaic` - Get random thumbnails for mosaic

### Business Logic Layer (`py_home_gallery/media/`)

**scanner.py** - Directory scanning
- `scan_directory()` - Recursively scan directories for media files
- `list_subfolders()` - List all subfolders
- `get_sorted_files()` - Get sorted file list (default/random/new)
- `validate_and_get_folder_path()` - Validate folder paths with security checks
- Integrates with cache for performance

**thumbnails.py** - Thumbnail generation
- `generate_video_thumbnail()` - Generate thumbnail from video (middle frame)
- `ensure_thumbnail_exists()` - Ensure thumbnail exists, generate if needed
- Handles errors gracefully with fallbacks

**dimensions.py** - Media dimensions
- `get_media_dimensions()` - Extract width/height from images and videos
- Supports both images and videos

**utils.py** - Media utilities
- `is_image()` - Check if file is an image
- `is_video()` - Check if file is a video
- `is_media()` - Check if file is supported media
- `get_media_type()` - Get media type (image/video/unknown)

### Cross-Cutting Concerns (`py_home_gallery/utils/`)

**security.py** - Security utilities
- `is_safe_path()` - Validate paths against traversal attacks
- `get_safe_path()` - Safely join paths with validation
- `validate_media_extension()` - Validate file extensions
- `sanitize_filename()` - Sanitize filenames

**logger.py** - Logging system
- `configure_logging()` - Configure logging system
- `get_logger()` - Get logger instance for module
- Supports console and file logging
- Structured log format with timestamps

**cache.py** - Caching system
- `SimpleCache` - Thread-safe cache with TTL
- `get_directory_cache()` - Get directory cache instance
- `get_metadata_cache()` - Get metadata cache instance
- `@cached` decorator - Function result caching

**pagination.py** - Pagination utilities
- `paginate_items()` - Paginate list of items
- `get_pagination_info()` - Get pagination metadata

**metadata.py** - Metadata extraction
- `get_media_metadata()` - Extract metadata from media files
- `format_metadata_for_display()` - Format metadata for display
- Supports EXIF data, video metadata, file stats

**ffmpeg.py** - FFmpeg validation
- `check_ffmpeg()` - Check if FFmpeg is available
- Validates FFmpeg installation at startup

### Background Workers (`py_home_gallery/workers/`)

**thumbnail_worker.py** - Thumbnail generation worker
- `ThumbnailWorker` - Thread pool for background thumbnail generation
- `get_thumbnail_worker()` - Get global worker instance
- `shutdown_thumbnail_worker()` - Graceful shutdown
- Queue-based job processing

**preload.py** - Cache preloading
- `preload_thumbnails()` - Preload thumbnails in background
- `preload_all()` - Preload all thumbnails

### Application Setup (`py_home_gallery/`)

**app.py** - Flask application factory
- `create_app()` - Create and configure Flask application
- Registers all route blueprints
- Sets up caching and workers
- Configures logging
- Preloads cache on startup

**config.py** - Configuration management
- `Config` class - Configuration from CLI args and environment variables

**constants.py** - Application-wide constants
- Centralized magic numbers and configuration values
- Pagination defaults (items per page, limits)
- Thumbnail dimensions and aspect ratios
- Cache settings (TTL, prefixes, suffixes)
- Worker settings (threads, queue sizes)
- Server defaults (host, port)
- File type extensions
- Default dimensions for media types
- Path configurations
- `load_config()` - Load and validate configuration
- Supports command-line arguments and environment variables

## Data Flow

### Gallery Request Flow

```
1. User requests /gallery
   ↓
2. Flask Router → gallery.bp
   ↓
3. gallery() route handler
   ├─ Validates folder parameter (security check)
   ├─ Calls get_sorted_files() (uses cache)
   ├─ Filters by media type if specified
   ├─ Paginates results
   ├─ Adds dimensions to paginated items only
   ├─ Renders gallery.html template
   └─ Returns HTML response
```

### Thumbnail Request Flow

```
1. User requests /thumbnail/video.mp4
   ↓
2. Flask Router → media.bp
   ↓
3. serve_thumbnail() route handler
   ├─ Validates path (security check)
   ├─ Checks if thumbnail exists
   ├─ If exists: serves thumbnail
   ├─ If not exists:
   │   ├─ Adds job to worker queue
   │   └─ Returns placeholder URL
   └─ Worker generates thumbnail in background
```

### Browse API Flow

```
1. User requests /api/browse
   ↓
2. Flask Router → browse.bp
   ↓
3. browse_api() route handler
   ├─ Lists all subfolders
   ├─ For each folder:
   │   ├─ Scans folder for media files
   │   ├─ Filters for vertical images
   │   ├─ Selects random thumbnail
   │   └─ Counts media files
   ├─ Returns JSON response
   └─ Frontend renders 3D Cover Flow
```

## Design Patterns

### 1. Blueprint Pattern (Flask)
Routes are organized into blueprints for modularity:
```python
bp = Blueprint('gallery', __name__)

@bp.route('/gallery')
def gallery():
    ...
```

### 2. Factory Pattern (App Creation)
Application is created via factory function:
```python
def create_app(config):
    app = Flask(__name__)
    # ... configuration
    return app
```

### 3. Singleton Pattern (Logger & Cache)
Shared instances across modules:
```python
_loggers = {}

def get_logger(name):
    if name not in _loggers:
        _loggers[name] = setup_logger(name)
    return _loggers[name]
```

### 4. Strategy Pattern (Sorting)
Different sorting strategies:
```python
def get_sorted_files(media_root, folder_path, sort_by="default"):
    if sort_by == "random":
        random.shuffle(media)
    elif sort_by == "new":
        media = sorted(media, key=lambda x: os.path.getmtime(...))
    return media
```

### 5. Guard Clauses Pattern (Validation)
Early returns for validation:
```python
def serve_media(filename):
    if not validate_media_extension(filename):
        abort(400)
    
    file_path = get_safe_path(media_root, filename)
    if not file_path:
        abort(403)
    
    # ... continue processing
```

## Security Flow

All file access follows a multi-layer security approach:

```
1. Extension Validation
   ↓ (validate_media_extension)
2. Path Traversal Protection
   ↓ (get_safe_path)
3. File Existence Check
   ↓ (os.path.exists)
4. Permission Check
   ↓ (os.access)
5. Serve File
```

See [Security Guide](SECURITY.md) for detailed information.

## Caching Strategy

### Directory Cache
- Caches directory scan results
- TTL: 5 minutes (configurable)
- Key: MD5 hash of directory path
- Used by: `scanner.py`

### Metadata Cache
- Caches metadata extraction results
- TTL: 10 minutes (2x directory cache)
- Key: MD5 hash of file path
- Used by: `metadata.py`

### Cache Invalidation
- Manual invalidation via `invalidate_directory_cache()`
- Automatic expiration based on TTL
- Cache warming on application startup

See [Cache and Workers Guide](CACHE_AND_WORKERS.md) for details.

## Background Workers

### Thumbnail Worker
- Thread pool for thumbnail generation
- Queue-based job processing
- Prevents blocking main application thread
- Configurable thread count (default: 2)

### Worker Lifecycle
1. Worker starts on application startup (if enabled)
2. Jobs added to queue when thumbnail needed
3. Worker processes jobs in background
4. Graceful shutdown on application exit

See [Cache and Workers Guide](CACHE_AND_WORKERS.md) for details.

## Component Interactions

### Scanner → Cache
Scanner uses cache to avoid repeated filesystem scans:
```python
cache_key = cache_key_for_directory(directory)
cached_result = directory_cache.get(cache_key)
if cached_result:
    return cached_result
```

### Routes → Security
All routes validate inputs using security utilities:
```python
file_path = get_safe_path(media_root, filename)
if not file_path:
    abort(403)
```

### Routes → Logger
All routes log requests and errors:
```python
logger = get_logger(__name__)
logger.info(f"Request: {filename}")
```

### Media → Worker
Media routes queue thumbnail generation jobs:
```python
if not os.path.exists(thumbnail_path):
    thumbnail_worker.add_job(video_path, thumbnail_path)
    return placeholder_url
```

## Configuration Flow

```
1. Environment Variables (defaults)
   ↓
2. Config class initialization
   ↓
3. Command-line arguments (override)
   ↓
4. Validation
   ↓
5. Application configuration
```

Configuration is loaded in this order:
1. Default values
2. Environment variables
3. Command-line arguments (highest priority)

See [Configuration Guide](CONFIGURATION.md) for details.

## Error Handling Strategy

All modules follow consistent error handling:

1. **Validation** - Check inputs early
2. **Try-Catch** - Catch specific exceptions
3. **Logging** - Log errors with context
4. **Fallback** - Provide fallback values when possible
5. **Cleanup** - Ensure resource cleanup in `finally` blocks

See [Error Handling Guide](ERROR_HANDLING.md) for details.

## Logging Architecture

```
All Modules
    ↓
get_logger(__name__)
    ↓
Centralized Logger
    ├─ Console Handler (stdout)
    └─ File Handler (logs/app.log)
    ↓
Formatted Output
    timestamp - module - level - message
```

See [Logging Guide](LOGGING.md) for details.

## Type Safety

All modules use type hints for:
- Function parameters and return types
- Class attributes
- Type checking with mypy (optional)

Example:
```python
def scan_directory(directory: str) -> List[Tuple[str, str]]:
    ...
```

See [Development Guide](DEVELOPMENT.md#type-hints) for details.

## Related Documentation

- [Security Guide](SECURITY.md) - Security architecture
- [Cache and Workers Guide](CACHE_AND_WORKERS.md) - Performance features
- [Error Handling Guide](ERROR_HANDLING.md) - Error handling patterns
- [Logging Guide](LOGGING.md) - Logging system
- [Development Guide](DEVELOPMENT.md) - Development practices

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

