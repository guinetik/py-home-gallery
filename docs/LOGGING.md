# Logging System - Py Home Gallery

## Overview

Py Home Gallery uses a centralized logging system that provides structured logging with consistent formatting across all modules. Logs can be written to both console and file, with configurable log levels.

## Quick Start

### Basic Usage

```python
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Server started on port 8000")
logger.warning("File not found: photo.jpg")
logger.error("Failed to generate thumbnail")
```

### Configuration

Logging is configured automatically when the application starts via `configure_logging()` in `app.py`. Configuration options:

- **Log Level**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Log to File**: Enable/disable file logging
- **Log Directory**: Directory for log files (default: `./logs`)

## Log Levels

### DEBUG (10)
Detailed information for diagnosing problems. Typically used during development.

```python
logger.debug(f"Processing file: {filename}")
logger.debug(f"Cache hit for: {key}")
```

**When to use**: Detailed diagnostic information, cache operations, function entry/exit.

### INFO (20)
Confirmation that things are working as expected. General informational messages.

```python
logger.info(f"Server started on port {port}")
logger.info(f"Found {len(media)} media files")
logger.info(f"Scan complete: {len(media)} files found")
```

**When to use**: Application lifecycle events, successful operations, general information.

### WARNING (30)
Something unexpected happened, but the application continues to function.

```python
logger.warning(f"File not found: {filepath}")
logger.warning(f"Path traversal attempt detected: {user_input}")
logger.warning(f"Video too large ({file_size_mb:.2f}MB): {video_path}")
```

**When to use**: Recoverable errors, security events, performance warnings.

### ERROR (40)
An error occurred that prevented a specific function from executing.

```python
logger.error(f"Failed to generate thumbnail: {video_path}")
logger.error(f"Error processing file {file}: {e}")
logger.error(f"Permission denied: {file_path}")
```

**When to use**: Errors that prevent specific operations, file processing failures.

### CRITICAL (50)
A serious error occurred that may prevent the application from continuing.

```python
logger.critical("Out of memory!")
logger.critical("Configuration file missing!")
logger.critical(f"Cannot access directory: {directory}")
```

**When to use**: Critical system failures, unrecoverable errors.

## Log Format

### Standard Format

```
YYYY-MM-DD HH:MM:SS - module.name - LEVEL - message
```

### Example Output

```
2024-12-15 10:30:15 - py_home_gallery.scanner - INFO - Starting directory scan: /media
2024-12-15 10:30:16 - py_home_gallery.scanner - INFO - Scan complete: 1245 files found
2024-12-15 10:30:20 - py_home_gallery.media - WARNING - Path traversal attempt: ../../../etc/passwd
2024-12-15 10:30:25 - py_home_gallery.thumbnails - ERROR - Failed to generate thumbnail: video.mp4
```

### Format Components

- **Timestamp**: Date and time of the log event
- **Module Name**: Logger name (typically `__name__`)
- **Level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Message**: Log message content

## Configuration

### Application Startup

Logging is configured in `app.py` during application creation:

```python
from py_home_gallery.utils.logger import configure_logging

configure_logging(
    log_level=config.log_level,      # 'INFO', 'DEBUG', etc.
    log_to_file=config.log_to_file,  # True/False
    log_dir=config.log_dir           # './logs'
)
```

### Command-Line Configuration

```bash
# Set log level
python run.py --log-level DEBUG

# Disable file logging
python run.py --no-log-file

# Set log directory
python run.py --log-dir /var/log/gallery
```

### Environment Variables

```bash
export PY_HOME_GALLERY_LOG_LEVEL=DEBUG
export PY_HOME_GALLERY_LOG_TO_FILE=true
export PY_HOME_GALLERY_LOG_DIR=./logs
```

## Log File Location

### Default Location

- **Directory**: `./logs`
- **File**: `logs/app.log`

### Custom Location

Set via `--log-dir` argument or `PY_HOME_GALLERY_LOG_DIR` environment variable.

The log directory is created automatically if it doesn't exist.

## Usage Examples

### Scanner Module

```python
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

def scan_directory(directory: str):
    logger.info(f"Starting directory scan: {directory}")
    
    try:
        # ... scanning logic ...
        
        logger.info(f"Scan complete: {len(media)} files found")
        return media
    
    except PermissionError:
        logger.error(f"Cannot access directory: {directory}")
        raise
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        raise
```

### Route Handler

```python
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

@bp.route('/media/<path:filename>')
def serve_media(filename):
    logger.debug(f"Media request: {filename}")
    
    if not validate_media_extension(filename):
        logger.warning(f"Invalid extension requested: {filename}")
        abort(400)
    
    file_path = get_safe_path(media_root, filename)
    if not file_path:
        logger.warning(f"Path traversal attempt: {filename}")
        abort(403)
    
    logger.info(f"Serving file: {filename}")
    return send_file(file_path)
```

### Error Handling with Stack Traces

```python
try:
    process_file(file_path)
except Exception as e:
    logger.error(f"Error processing {file_path}: {e}", exc_info=True)
    # exc_info=True includes full stack trace
```

## Log Filtering and Analysis

### Filter by Level

```bash
# Show only errors
grep "ERROR" logs/app.log

# Show warnings and errors
grep -E "WARNING|ERROR|CRITICAL" logs/app.log
```

### Filter by Module

```bash
# Show only scanner logs
grep "scanner" logs/app.log

# Show only route logs
grep -E "gallery|media|browse" logs/app.log
```

### Security Analysis

```bash
# Find path traversal attempts
grep "Path traversal" logs/app.log

# Find access denied events
grep "Access denied" logs/app.log

# Find invalid extension requests
grep "Invalid extension" logs/app.log
```

### Performance Analysis

```bash
# Find slow operations
grep "took" logs/app.log

# Find cache operations
grep -E "Cache HIT|Cache MISS" logs/app.log
```

### Count Errors by Module

```bash
grep "ERROR" logs/app.log | cut -d'-' -f3 | sort | uniq -c
```

## Best Practices

### 1. Use Module-Specific Loggers

Always use `get_logger(__name__)` to get a logger for your module:

```python
# ✅ Good
logger = get_logger(__name__)

# ❌ Avoid
logger = get_logger('app')
```

### 2. Include Context in Messages

Provide context in log messages:

```python
# ✅ Good
logger.error(f"Failed to process {filename} in {directory}: {error}")

# ❌ Bad
logger.error("Failed")
```

### 3. Use Appropriate Log Levels

Choose the right log level for each message:

```python
logger.debug("Cache miss")              # Debug information
logger.info("Server started")           # Normal operation
logger.warning("Config not found")      # Warning condition
logger.error("Database error")         # Error condition
logger.critical("Out of memory")        # Critical failure
```

### 4. Don't Log Sensitive Information

Never log passwords, API keys, or other sensitive data:

```python
# ✅ Good
logger.info(f"User logged in: {username}")

# ❌ Bad
logger.info(f"Password attempt: {password}")
```

### 5. Use Lazy Formatting for Performance

For DEBUG level logs, use lazy formatting:

```python
# ✅ Good (lazy formatting)
logger.debug("Processing %s", filename)

# ⚠️ OK for INFO+ (eager formatting is fine)
logger.info(f"Processing {filename}")
```

### 6. Include Exception Information

When logging exceptions, include the exception object:

```python
try:
    process_file(file_path)
except Exception as e:
    logger.error(f"Error processing {file_path}: {e}", exc_info=True)
```

## Log Rotation (Future Enhancement)

For production deployments, consider implementing log rotation:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
```

This prevents log files from growing indefinitely.

## Monitoring

### Real-Time Monitoring

```bash
# Follow log file in real-time
tail -f logs/app.log

# Follow with filtering
tail -f logs/app.log | grep ERROR
```

### Log Analysis Tools

Consider using log analysis tools for production:
- **grep/awk**: Basic filtering and analysis
- **logrotate**: Automatic log rotation
- **ELK Stack**: Elasticsearch, Logstash, Kibana (for large deployments)
- **Splunk**: Enterprise log analysis

## Configuration Options

### Available Options

| Option | CLI Argument | Environment Variable | Default |
|--------|--------------|---------------------|---------|
| Log Level | `--log-level` | `PY_HOME_GALLERY_LOG_LEVEL` | `INFO` |
| Log to File | `--no-log-file` | `PY_HOME_GALLERY_LOG_TO_FILE` | `true` |
| Log Directory | `--log-dir` | `PY_HOME_GALLERY_LOG_DIR` | `./logs` |

### Log Level Values

- `DEBUG` - Most verbose
- `INFO` - Default, normal operation
- `WARNING` - Warnings only
- `ERROR` - Errors only
- `CRITICAL` - Critical errors only

## Troubleshooting

### Logs Not Appearing

1. **Check log level**: Ensure log level allows your messages
   ```bash
   python run.py --log-level DEBUG
   ```

2. **Check file permissions**: Ensure log directory is writable
   ```bash
   chmod 755 logs
   ```

3. **Check configuration**: Verify logging is enabled
   ```bash
   python run.py --log-level INFO
   ```

### Log File Too Large

1. **Increase log level**: Reduce verbosity
   ```bash
   python run.py --log-level WARNING
   ```

2. **Disable file logging**: Log only to console
   ```bash
   python run.py --no-log-file
   ```

3. **Implement log rotation**: See Log Rotation section above

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Error Handling Guide](ERROR_HANDLING.md) - Error handling patterns
- [Security Guide](SECURITY.md) - Security logging
- [Configuration Guide](CONFIGURATION.md) - Configuration options

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

