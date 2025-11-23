# Error Handling - Py Home Gallery

## Overview

Py Home Gallery implements comprehensive error handling strategies to ensure the application remains stable and provides useful feedback even when errors occur. Errors are handled gracefully with appropriate logging and user-facing messages.

## Error Handling Strategies

### 1. Validation Before Processing

Always validate inputs before performing expensive operations:

```python
def scan_directory(directory: str) -> List[Tuple[str, str]]:
    # Validate directory exists
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return []
    
    # Validate it's a directory
    if not os.path.isdir(directory):
        logger.warning(f"Path is not a directory: {directory}")
        return []
    
    # Continue with processing...
```

### 2. Granular Try-Catch Blocks

Catch errors at the appropriate level - per file rather than per operation:

```python
for root, _, files in os.walk(directory):
    for file in files:
        try:
            # Process individual file
            process_file(file)
        except PermissionError:
            logger.warning(f"Permission denied: {file}")
            continue  # Continue with next file
        except Exception as e:
            logger.error(f"Error processing {file}: {e}")
            continue  # Continue with next file
```

### 3. Graceful Fallbacks

Provide fallback values when operations fail:

```python
def ensure_thumbnail_exists(video_path: str, thumbnail_path: str, placeholder_url: str) -> str:
    try:
        # Try to generate thumbnail
        if generate_video_thumbnail(video_path, thumbnail_path):
            return thumbnail_path
        
        # Fallback to placeholder
        logger.debug(f"Using placeholder for: {video_path}")
        return placeholder_url
    
    except Exception as e:
        logger.error(f"Error ensuring thumbnail: {e}")
        return placeholder_url or ""
```

### 4. Resource Cleanup

Always ensure resources are cleaned up, even when errors occur:

```python
def generate_video_thumbnail(video_path: str, thumbnail_path: str) -> bool:
    clip = None
    
    try:
        clip = VideoFileClip(video_path)
        # ... process video ...
        return True
    
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return False
    
    finally:
        # Always cleanup, even if error occurred
        if clip is not None:
            try:
                clip.close()
            except Exception as e:
                logger.warning(f"Error closing clip: {e}")
```

### 5. Specific Error Messages

Provide specific error messages with appropriate HTTP status codes:

```python
@bp.route('/media/<path:filename>')
def serve_media(filename):
    try:
        # Validation 1: Extension
        if not validate_media_extension(filename):
            logger.warning(f"Invalid extension: {filename}")
            abort(400, description="Invalid file type")
        
        # Validation 2: Path traversal
        file_path = get_safe_path(media_root, filename)
        if not file_path:
            logger.warning(f"Path traversal attempt: {filename}")
            abort(403, description="Access denied")
        
        # Validation 3: File exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            abort(404, description="File not found")
        
        # Validation 4: Permissions
        if not os.access(file_path, os.R_OK):
            logger.error(f"Permission denied: {file_path}")
            abort(403, description="Permission denied")
        
        # Serve file
        return send_file(file_path)
    
    except Exception as e:
        logger.error(f"Error serving {filename}: {e}")
        abort(500, description="Internal server error")
```

## Error Categories

### 400 Bad Request - Invalid Input

User provided invalid input (wrong file type, malformed request, etc.):

```python
if not validate_media_extension(filename):
    logger.warning(f"Invalid extension: {filename}")
    abort(400, description="Invalid file type")
```

**When to use**: Invalid user input, malformed requests, unsupported file types.

### 403 Forbidden - Access Denied

User attempted to access a resource they don't have permission for:

```python
file_path = get_safe_path(media_root, filename)
if not file_path:
    logger.warning(f"Path traversal attempt: {filename}")
    abort(403, description="Access denied")

if not os.access(file_path, os.R_OK):
    logger.error(f"Permission denied: {file_path}")
    abort(403, description="Permission denied")
```

**When to use**: Path traversal attempts, permission denied, unauthorized access.

### 404 Not Found - Resource Not Found

Requested resource doesn't exist:

```python
if not os.path.exists(file_path):
    logger.warning(f"File not found: {file_path}")
    abort(404, description="File not found")
```

**When to use**: File not found, directory not found, missing resources.

### 500 Internal Server Error

Unexpected server error:

```python
try:
    result = process_data()
except Exception as e:
    logger.error(f"Internal error: {e}", exc_info=True)
    abort(500, description="Internal server error")
```

**When to use**: Unexpected errors, system failures, unhandled exceptions.

## Error Handling by Module

### Scanner Module (`media/scanner.py`)

**Strategy**: Continue processing even if individual files fail.

```python
def scan_directory(directory: str) -> List[Tuple[str, str]]:
    media = []
    scanned_files = 0
    skipped_files = 0
    errors = 0
    
    logger.info(f"Starting scan: {directory}")
    
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                scanned_files += 1
                
                try:
                    # Validate extension
                    if not validate_media_extension(file):
                        skipped_files += 1
                        continue
                    
                    full_path = os.path.join(root, file)
                    
                    # Validate existence
                    if not os.path.exists(full_path):
                        logger.warning(f"Broken symlink: {full_path}")
                        errors += 1
                        continue
                    
                    # Validate permissions
                    if not os.access(full_path, os.R_OK):
                        logger.warning(f"Permission denied: {full_path}")
                        errors += 1
                        continue
                    
                    # Process file
                    media.append((rel_path, thumb_path))
                
                except PermissionError:
                    logger.warning(f"Permission denied: {file}")
                    errors += 1
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")
                    errors += 1
    
    except PermissionError:
        logger.error(f"Cannot access directory: {directory}")
        raise
    except Exception as e:
        logger.error(f"Error scanning: {e}")
        raise
    
    # Log summary
    logger.info(f"Scan complete: {len(media)} found, {skipped_files} skipped, {errors} errors")
    
    return media
```

### Thumbnail Generation (`media/thumbnails.py`)

**Strategy**: Validate before processing, cleanup on error, return False on failure.

```python
def generate_video_thumbnail(video_path: str, thumbnail_path: str) -> bool:
    clip = None
    
    try:
        # Validate file exists
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return False
        
        # Validate file size (prevent OOM)
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > 500:
            logger.warning(f"Video too large ({file_size_mb:.2f}MB): {video_path}")
            return False
        
        # Process video
        clip = VideoFileClip(video_path)
        
        if clip.duration <= 0:
            logger.warning(f"Invalid duration: {video_path}")
            return False
        
        # Generate thumbnail
        frame = clip.get_frame(clip.duration / 2)
        clip.close()
        clip = None
        
        # Save thumbnail
        image = Image.fromarray(frame)
        image.save(thumbnail_path, 'PNG', optimize=True)
        
        logger.info(f"Thumbnail generated: {thumbnail_path}")
        return True
    
    except MemoryError:
        logger.error(f"Out of memory: {video_path}")
        return False
    except PermissionError:
        logger.error(f"Permission denied: {video_path}")
        return False
    except OSError as e:
        logger.error(f"OS error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        # Always cleanup
        if clip is not None:
            try:
                clip.close()
            except:
                pass
```

### Route Handlers (`routes/media.py`)

**Strategy**: Validate inputs, catch specific errors, return appropriate HTTP status codes.

```python
@bp.route('/media/<path:filename>')
def serve_media(filename):
    try:
        logger.debug(f"Request: {filename}")
        
        # Layer 1: Extension validation
        if not validate_media_extension(filename):
            logger.warning(f"Invalid extension: {filename}")
            abort(400, description="Invalid file type")
        
        # Layer 2: Path traversal protection
        file_path = get_safe_path(media_root, filename)
        if not file_path:
            logger.warning(f"Path traversal: {filename}")
            abort(403, description="Access denied")
        
        # Layer 3: File existence
        if not os.path.exists(file_path):
            logger.warning(f"Not found: {file_path}")
            abort(404, description="File not found")
        
        # Layer 4: Permissions
        if not os.access(file_path, os.R_OK):
            logger.error(f"Permission denied: {file_path}")
            abort(403, description="Permission denied")
        
        # Serve file
        logger.info(f"Serving: {filename}")
        return send_file(file_path)
    
    except Exception as e:
        logger.error(f"Error serving {filename}: {e}", exc_info=True)
        abort(500, description="Internal server error")
```

## Best Practices

### 1. Validate Early

Check inputs before performing expensive operations:

```python
# ✅ Good: Validate before processing
if not os.path.exists(path):
    return None

result = expensive_operation(path)
```

### 2. Catch Specific Exceptions

Catch specific exception types when possible:

```python
# ✅ Good: Catch specific exceptions
try:
    file = open(path)
except FileNotFoundError:
    logger.warning("File not found")
except PermissionError:
    logger.error("Permission denied")
except Exception as e:
    logger.error(f"Unexpected: {e}")
```

### 3. Never Swallow Errors Silently

Always log errors, even if you continue processing:

```python
# ❌ Bad: Silent failure
try:
    process()
except:
    pass

# ✅ Good: Log and continue
try:
    process()
except Exception as e:
    logger.error(f"Error: {e}")
    return default_value
```

### 4. Provide Context

Include context in error messages:

```python
# ❌ Bad: Generic message
logger.error("Error occurred")

# ✅ Good: Context included
logger.error(f"Error processing {filename} in {directory}: {error}")
```

### 5. Ensure Cleanup

Use `finally` blocks to ensure resource cleanup:

```python
# ✅ Good: Cleanup guaranteed
resource = None
try:
    resource = acquire_resource()
    use_resource(resource)
finally:
    if resource:
        release_resource(resource)
```

### 6. Don't Expose Internal Details

Error messages should not expose internal implementation details:

```python
# ❌ Bad: Exposes internal path
abort(404, f"File not found: {internal_path}")

# ✅ Good: Generic message
abort(404, description="File not found")
```

### 7. Log with Appropriate Levels

Use appropriate log levels for different error types:

```python
logger.debug("Cache miss")              # Debug information
logger.info("Operation completed")     # Normal operation
logger.warning("File not found")       # Warning condition
logger.error("Processing failed")      # Error condition
logger.critical("System failure")      # Critical failure
```

## Error Recovery Patterns

### Pattern 1: Continue on Error

Continue processing remaining items when one fails:

```python
for item in items:
    try:
        process(item)
    except Exception as e:
        logger.error(f"Error processing {item}: {e}")
        continue  # Continue with next item
```

### Pattern 2: Fallback Value

Provide a fallback when operation fails:

```python
try:
    thumbnail = generate_thumbnail(video)
except Exception as e:
    logger.warning(f"Using placeholder: {e}")
    thumbnail = placeholder_url
```

### Pattern 3: Retry with Backoff

Retry operation with exponential backoff:

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        result = operation()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        wait_time = 2 ** attempt
        logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
        time.sleep(wait_time)
```

### Pattern 4: Graceful Degradation

Provide reduced functionality when full operation fails:

```python
try:
    dimensions = get_dimensions(file)
except Exception as e:
    logger.warning(f"Using default dimensions: {e}")
    dimensions = (300, 200)  # Default dimensions
```

## Error Metrics

Track error rates for monitoring:

```python
def scan_directory(directory: str) -> List[Tuple[str, str]]:
    total = 0
    success = 0
    errors = 0
    
    for file in files:
        total += 1
        try:
            process(file)
            success += 1
        except Exception as e:
            errors += 1
            logger.error(f"Error: {e}")
    
    error_rate = (errors / total * 100) if total > 0 else 0
    logger.info(f"Error rate: {error_rate:.2f}%")
    
    # Alert on high error rates
    if error_rate > 10:
        logger.warning(f"High error rate: {error_rate:.2f}%")
    if error_rate > 50:
        logger.critical(f"Critical error rate: {error_rate:.2f}%")
```

## Debugging Errors

### Include Stack Traces

Include full stack traces for debugging:

```python
try:
    process()
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)  # Includes stack trace
```

### Context Managers for Debugging

Use context managers to track operation timing:

```python
import contextlib
import time

@contextlib.contextmanager
def timer(operation: str):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.debug(f"{operation} took {duration:.2f}s")

# Usage
with timer("Scan directory"):
    scan_directory(path)
```

## Related Documentation

- [Logging Guide](LOGGING.md) - Logging system
- [Security Guide](SECURITY.md) - Security error handling
- [Architecture Guide](ARCHITECTURE.md) - System architecture

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

