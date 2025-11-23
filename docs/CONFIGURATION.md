# Configuration Guide - Py Home Gallery

## Overview

Py Home Gallery can be configured via command-line arguments, environment variables, or a combination of both. Command-line arguments take precedence over environment variables.

## Configuration Priority

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Default values** (lowest priority)

## Command-Line Arguments

### Basic Options

#### `--media-dir PATH`
Root directory containing media files.

**Default**: `./media`  
**Environment Variable**: `PY_HOME_GALLERY_MEDIA_DIR`

**Examples**:
```bash
# Linux/macOS
python run.py --media-dir "/home/user/Media"

# Windows (PowerShell)
python run.py --media-dir "C:\Users\user\Media"

# Windows (CMD)
python run.py --media-dir "C:\Users\user\Media"
```

#### `--thumbnail-dir PATH`
Directory to store generated thumbnails.

**Default**: 
- Linux/macOS: `~/.py-home-gallery/thumbnails`
- Windows: `C:\Users\YourUsername\.py-home-gallery\thumbnails`

**Environment Variable**: `PY_HOME_GALLERY_THUMB_DIR`

**Examples**:
```bash
python run.py --thumbnail-dir "/custom/path/thumbnails"
```

#### `--items-per-page NUM`
Number of items to display per page.

**Default**: `50`  
**Environment Variable**: `PY_HOME_GALLERY_ITEMS_PER_PAGE`

**Examples**:
```bash
python run.py --items-per-page 100
```

#### `--host HOST`
Host to run the server on.

**Default**: `0.0.0.0` (all interfaces)  
**Environment Variable**: `PY_HOME_GALLERY_HOST`

**Examples**:
```bash
# Listen on all interfaces
python run.py --host 0.0.0.0

# Listen on localhost only
python run.py --host 127.0.0.1
```

#### `--port PORT`
Port to run the server on.

**Default**: `8000`  
**Environment Variables**: `PY_HOME_GALLERY_PORT` or `PORT`

**Examples**:
```bash
python run.py --port 8080
```

#### `--placeholder URL`
URL for placeholder thumbnails.

**Default**: `https://via.placeholder.com/300x200`  
**Environment Variable**: `PY_HOME_GALLERY_PLACEHOLDER`

**Examples**:
```bash
python run.py --placeholder "https://example.com/placeholder.jpg"
```

### Performance Options

#### `--cache-ttl SECONDS`
Cache TTL (Time To Live) in seconds.

**Default**: `300` (5 minutes)  
**Environment Variable**: `PY_HOME_GALLERY_CACHE_TTL`

**Examples**:
```bash
# Cache for 10 minutes
python run.py --cache-ttl 600

# Cache for 1 minute
python run.py --cache-ttl 60
```

#### `--worker-threads NUM`
Number of background worker threads for thumbnail generation.

**Default**: `2`  
**Environment Variable**: `PY_HOME_GALLERY_WORKER_THREADS`

**Examples**:
```bash
# Use 4 worker threads
python run.py --worker-threads 4
```

#### `--no-cache`
Disable caching.

**Environment Variable**: `PY_HOME_GALLERY_CACHE_ENABLED=false`

**Examples**:
```bash
python run.py --no-cache
```

#### `--no-worker`
Disable background thumbnail generation workers.

**Environment Variable**: `PY_HOME_GALLERY_WORKER_ENABLED=false`

**Examples**:
```bash
python run.py --no-worker
```

### Logging Options

#### `--log-level LEVEL`
Logging level.

**Default**: `INFO`  
**Environment Variable**: `PY_HOME_GALLERY_LOG_LEVEL`

**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Examples**:
```bash
python run.py --log-level DEBUG
```

#### `--no-log-file`
Disable logging to file (log to console only).

**Environment Variable**: `PY_HOME_GALLERY_LOG_TO_FILE=false`

**Examples**:
```bash
python run.py --no-log-file
```

#### `--log-dir PATH`
Directory for log files.

**Default**: `./logs`  
**Environment Variable**: `PY_HOME_GALLERY_LOG_DIR`

**Examples**:
```bash
python run.py --log-dir "/var/log/gallery"
```

### Production Options

#### `--production`
Run in production mode using Waitress WSGI server.

**Environment Variable**: `PY_HOME_GALLERY_PRODUCTION=true`

**Note**: Requires `waitress` package (`pip install waitress`)

**Examples**:
```bash
python run.py --production
```

#### `--no-serve-media`
Disable Flask media file serving (for use with external server like Nginx).

**Environment Variable**: `PY_HOME_GALLERY_SERVE_MEDIA=false`

**Examples**:
```bash
python run.py --no-serve-media
```

### Other Options

#### `--skip-ffmpeg-check`
Skip the check for FFmpeg installation.

**Warning**: Use at your own risk. Video thumbnails will fail if FFmpeg is not available.

**Examples**:
```bash
python run.py --skip-ffmpeg-check
```

## Environment Variables

### Setting Environment Variables

#### Linux/macOS (Bash)

```bash
export PY_HOME_GALLERY_MEDIA_DIR="/path/to/media"
export PY_HOME_GALLERY_PORT=8080
export PY_HOME_GALLERY_CACHE_TTL=600
python run.py
```

#### Windows (PowerShell)

```powershell
$env:PY_HOME_GALLERY_MEDIA_DIR = "C:\path\to\media"
$env:PY_HOME_GALLERY_PORT = "8080"
$env:PY_HOME_GALLERY_CACHE_TTL = "600"
python run.py
```

#### Windows (CMD)

```cmd
SET PY_HOME_GALLERY_MEDIA_DIR=C:\path\to\media
SET PY_HOME_GALLERY_PORT=8080
SET PY_HOME_GALLERY_CACHE_TTL=600
python run.py
```

### Complete List of Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PY_HOME_GALLERY_MEDIA_DIR` | Media directory path | `./media` |
| `PY_HOME_GALLERY_THUMB_DIR` | Thumbnail directory | `~/.py-home-gallery/thumbnails` |
| `PY_HOME_GALLERY_ITEMS_PER_PAGE` | Items per page | `50` |
| `PY_HOME_GALLERY_HOST` | Server host | `0.0.0.0` |
| `PY_HOME_GALLERY_PORT` | Server port | `8000` |
| `PORT` | Server port (alternative) | `8000` |
| `PY_HOME_GALLERY_PLACEHOLDER` | Placeholder URL | `https://via.placeholder.com/300x200` |
| `PY_HOME_GALLERY_CACHE_ENABLED` | Enable cache | `true` |
| `PY_HOME_GALLERY_CACHE_TTL` | Cache TTL (seconds) | `300` |
| `PY_HOME_GALLERY_WORKER_ENABLED` | Enable workers | `true` |
| `PY_HOME_GALLERY_WORKER_THREADS` | Worker threads | `2` |
| `PY_HOME_GALLERY_LOG_LEVEL` | Log level | `INFO` |
| `PY_HOME_GALLERY_LOG_TO_FILE` | Log to file | `true` |
| `PY_HOME_GALLERY_LOG_DIR` | Log directory | `./logs` |
| `PY_HOME_GALLERY_PRODUCTION` | Production mode | `false` |
| `PY_HOME_GALLERY_SERVE_MEDIA` | Serve media files | `true` |

## Configuration Examples

### Basic Usage

```bash
# Simple setup with just media directory
python run.py --media-dir "/path/to/media"
```

### Custom Port and Items Per Page

```bash
python run.py \
  --media-dir "/path/to/media" \
  --port 8080 \
  --items-per-page 100
```

### Development Configuration

```bash
# Development: no cache, debug logging, fewer items
python run.py \
  --media-dir "./samplegallery" \
  --no-cache \
  --log-level DEBUG \
  --items-per-page 20
```

### Production Configuration

```bash
# Production: optimized performance
python run.py \
  --media-dir "/media/gallery" \
  --port 8000 \
  --cache-ttl 600 \
  --worker-threads 4 \
  --log-level INFO \
  --production
```

### Docker Configuration

```yaml
# docker-compose.yml
environment:
  - PY_HOME_GALLERY_MEDIA_DIR=/media
  - PY_HOME_GALLERY_THUMB_DIR=/thumbnails
  - PY_HOME_GALLERY_PORT=5000
  - PY_HOME_GALLERY_CACHE_ENABLED=true
  - PY_HOME_GALLERY_CACHE_TTL=300
  - PY_HOME_GALLERY_WORKER_ENABLED=true
  - PY_HOME_GALLERY_WORKER_THREADS=2
  - PY_HOME_GALLERY_LOG_LEVEL=INFO
```

## Platform-Specific Notes

### Windows Path Syntax

#### Command Prompt (CMD)

```cmd
# Use environment variables with percent signs
python run.py --media-dir "%USERPROFILE%\Media"

# Escape backslashes by doubling them
python run.py --media-dir "C:\\Users\\user\\Media"

# Or use forward slashes
python run.py --media-dir "C:/Users/user/Media"
```

#### PowerShell

```powershell
# Use environment variables with $env:
python run.py --media-dir "$env:USERPROFILE\Media"

# Use forward slashes to avoid escape issues
python run.py --media-dir "C:/Users/user/Media"
```

**Note**: The tilde (`~`) shorthand for home directory doesn't work in Windows. Use `%USERPROFILE%` (CMD) or `$env:USERPROFILE` (PowerShell) instead.

### Linux/macOS

```bash
# Use tilde for home directory
python run.py --media-dir "~/Media"

# Or absolute path
python run.py --media-dir "/home/user/Media"
```

## Configuration Validation

The application validates configuration on startup:

1. **Media Directory**: Must exist and be a directory
2. **Thumbnail Directory**: Created if doesn't exist
3. **Log Directory**: Created if logging to file enabled
4. **FFmpeg**: Checked unless `--skip-ffmpeg-check` is used

### Validation Errors

If validation fails, the application will exit with an error message:

```
Error: Media directory '/invalid/path' does not exist.
```

## Configuration Display

The application displays current configuration on startup:

```
Media Gallery Server Configuration:
Media Directory: /path/to/media
Thumbnail Directory: /path/to/thumbnails
Items Per Page: 50
Host: 0.0.0.0
Port: 8000
Production Mode: False
Serve Media: True
Cache Enabled: True (TTL: 300s)
Background Workers: 2
Log Level: INFO
Log to File: True (Dir: ./logs)
```

## Best Practices

### Development

- Use `--no-cache` to see changes immediately
- Use `--log-level DEBUG` for detailed logging
- Use `--no-worker` for simpler debugging

### Production

- Use appropriate cache TTL (300-600 seconds)
- Enable workers with 2-4 threads
- Use `--production` mode with Waitress
- Set `--no-serve-media` if using Nginx
- Use `--log-level INFO` or `WARNING`

### Docker

- Use environment variables in `docker-compose.yml`
- Set `PY_HOME_GALLERY_SERVE_MEDIA=false` when using Nginx
- Configure appropriate cache and worker settings

## Troubleshooting

### Configuration Not Applied

1. **Check priority**: Command-line arguments override environment variables
2. **Check syntax**: Ensure correct format for your platform
3. **Check validation**: Ensure paths exist and are accessible

### Path Issues

1. **Windows**: Use forward slashes or escaped backslashes
2. **Spaces**: Quote paths with spaces
3. **Permissions**: Ensure read access to media directory

### Port Already in Use

```bash
# Check what's using the port
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Use a different port
python run.py --port 8080
```

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Cache and Workers Guide](CACHE_AND_WORKERS.md) - Performance configuration
- [Logging Guide](LOGGING.md) - Logging configuration

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

