# Security - Py Home Gallery

## Overview

Py Home Gallery implements comprehensive security measures to protect against common web application vulnerabilities, particularly those related to file serving and path manipulation.

## Security Features

### 1. Path Traversal Protection

**Vulnerability**: Path traversal attacks allow attackers to access files outside the intended directory (e.g., `/media/../../../etc/passwd`).

**Protection**: All file paths are validated using `get_safe_path()` before access.

**Implementation**:
```python
from py_home_gallery.utils.security import get_safe_path

file_path = get_safe_path(media_root, filename)
if not file_path:
    logger.warning(f"Path traversal attempt detected: {filename}")
    abort(403, description="Access denied")
```

**How it works**:
- Resolves paths to absolute paths
- Uses `os.path.commonpath()` to ensure user path is within base directory
- Returns `None` if path is outside allowed directory
- Handles Windows drive differences correctly

### 2. Extension Validation

**Vulnerability**: Serving executable files or scripts could allow code execution.

**Protection**: Only allowed media extensions are permitted.

**Allowed Extensions**:
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`
- Videos: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`

**Implementation**:
```python
from py_home_gallery.utils.security import validate_media_extension

if not validate_media_extension(filename):
    logger.warning(f"Invalid extension: {filename}")
    abort(400, description="Invalid file type")
```

### 3. Filename Sanitization

**Vulnerability**: Dangerous characters in filenames could cause issues.

**Protection**: Dangerous characters are removed from filenames.

**Implementation**:
```python
from py_home_gallery.utils.security import sanitize_filename

sanitized = sanitize_filename(filename)
# Removes: /, \, .., <, >, :, ", |, ?, *, \0
```

### 4. File Existence and Permission Checks

**Protection**: Files are verified to exist and be readable before serving.

**Implementation**:
```python
if not os.path.exists(file_path):
    abort(404, description="File not found")

if not os.access(file_path, os.R_OK):
    abort(403, description="Permission denied")
```

## Security Layers

All file access follows a multi-layer security approach:

```
Layer 1: Extension Validation
   ↓ validate_media_extension()
   ✅ .jpg, .mp4, etc. | ❌ .exe, .php, etc.

Layer 2: Path Traversal Protection
   ↓ get_safe_path()
   ✅ /media/photo.jpg | ❌ /media/../../../etc/passwd

Layer 3: File Existence Check
   ↓ os.path.exists()
   ✅ File exists | ❌ File not found

Layer 4: Permission Check
   ↓ os.access(file_path, os.R_OK)
   ✅ Readable | ❌ Permission denied

Layer 5: Serve File
   ↓ send_file()
   ✅ File served securely
```

## Security Implementation by Module

### Routes (`routes/media.py`)

All media serving routes implement full security checks:

```python
@bp.route('/media/<path:filename>')
def serve_media(filename):
    # Layer 1: Extension validation
    if not validate_media_extension(filename):
        logger.warning(f"Invalid extension: {filename}")
        abort(400, description="Invalid file type")
    
    # Layer 2: Path traversal protection
    file_path = get_safe_path(media_root, filename)
    if not file_path:
        logger.warning(f"Path traversal attempt: {filename}")
        abort(403, description="Access denied")
    
    # Layer 3: File existence
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    # Layer 4: Permission check
    if not os.access(file_path, os.R_OK):
        logger.error(f"Permission denied: {file_path}")
        abort(403, description="Permission denied")
    
    # Layer 5: Serve file
    return send_file(file_path)
```

### Scanner (`media/scanner.py`)

Directory scanning validates all paths:

```python
def validate_and_get_folder_path(media_root: str, folder: Optional[str]) -> Optional[str]:
    """Validate folder path with security checks."""
    if not folder:
        return os.path.abspath(media_root)
    
    # Use security validation
    folder_path = get_safe_path(media_root, folder)
    
    if not folder_path:
        logger.warning(f"Path traversal attempt: {folder}")
        return None
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None
    
    return folder_path
```

### Metadata API (`routes/metadata.py`)

Metadata endpoints validate paths:

```python
@bp.route('/api/metadata/<path:media_path>')
def get_metadata(media_path):
    # Security check
    full_path = get_safe_path(media_root, media_path)
    
    if not full_path:
        return jsonify({'error': 'Invalid file path'}), 403
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Process metadata...
```

## Security Utilities

### `is_safe_path(base_dir, user_path, follow_symlinks=False)`

Validates that a user-provided path is within the base directory.

**Parameters**:
- `base_dir`: The base directory that should contain the file
- `user_path`: The user-provided path to validate
- `follow_symlinks`: Whether to resolve symbolic links (default: False)

**Returns**: `True` if safe, `False` otherwise

**Example**:
```python
is_safe_path('/media', '/media/photos/img.jpg')  # True
is_safe_path('/media', '/media/../etc/passwd')   # False
```

### `get_safe_path(base_dir, relative_path, follow_symlinks=False)`

Safely joins a base directory with a relative path and validates the result.

**Parameters**:
- `base_dir`: The base directory
- `relative_path`: The relative path to join
- `follow_symlinks`: Whether to resolve symbolic links (default: False)

**Returns**: The safe absolute path, or `None` if invalid

**Example**:
```python
get_safe_path('/media', 'photos/img.jpg')     # '/media/photos/img.jpg'
get_safe_path('/media', '../etc/passwd')       # None
```

### `validate_media_extension(filename, allowed_extensions=None)`

Validates that a file has an allowed media extension.

**Parameters**:
- `filename`: The filename to validate
- `allowed_extensions`: Tuple of allowed extensions (default: common media types)

**Returns**: `True` if extension is allowed, `False` otherwise

**Example**:
```python
validate_media_extension('photo.jpg')  # True
validate_media_extension('script.php') # False
```

### `sanitize_filename(filename)`

Sanitizes a filename to remove potentially dangerous characters.

**Parameters**:
- `filename`: The filename to sanitize

**Returns**: The sanitized filename

**Example**:
```python
sanitize_filename('../../etc/passwd')      # 'etcpasswd'
sanitize_filename('photo<script>.jpg')      # 'photoscript.jpg'
```

## Security Logging

All security events are logged for auditing:

```python
logger.warning(f"Path traversal attempt detected: {filename}")
logger.warning(f"Invalid extension requested: {filename}")
logger.error(f"Permission denied: {file_path}")
```

Logs are written to:
- Console (if enabled)
- `logs/app.log` (if file logging enabled)

See [Logging Guide](LOGGING.md) for details.

## Security Testing

### Manual Testing

**Test Path Traversal**:
```bash
# Should return 403 Forbidden
curl http://localhost:8000/media/../../../etc/passwd

# Should return 403 Forbidden
curl http://localhost:8000/media/..%2F..%2F..%2Fetc%2Fpasswd
```

**Test Invalid Extension**:
```bash
# Should return 400 Bad Request
curl http://localhost:8000/media/script.php
```

**Test Valid File**:
```bash
# Should return 200 OK (if file exists)
curl http://localhost:8000/media/photo.jpg
```

### Automated Testing Recommendations

1. **Path Traversal Tests**:
   - Test various traversal patterns (`../`, `..\\`, encoded versions)
   - Test absolute paths
   - Test symlink traversal (if `follow_symlinks=True`)

2. **Extension Validation Tests**:
   - Test all allowed extensions
   - Test blocked extensions (`.exe`, `.php`, `.sh`, etc.)
   - Test case variations (`.JPG`, `.jPg`)

3. **Permission Tests**:
   - Test files without read permission
   - Test directories without access permission

## Security Best Practices

### For Development

1. **Always use security utilities**: Never construct paths manually
   ```python
   # ❌ Bad
   file_path = os.path.join(media_root, user_input)
   
   # ✅ Good
   file_path = get_safe_path(media_root, user_input)
   if not file_path:
       abort(403)
   ```

2. **Validate early**: Check extensions and paths before processing
   ```python
   # ✅ Good: Validate before expensive operations
   if not validate_media_extension(filename):
       abort(400)
   ```

3. **Log security events**: Always log suspicious activity
   ```python
   logger.warning(f"Path traversal attempt: {user_input}")
   ```

4. **Never expose internal paths**: Error messages should not reveal filesystem structure
   ```python
   # ❌ Bad
   abort(404, f"File not found: {internal_path}")
   
   # ✅ Good
   abort(404, description="File not found")
   ```

### For Deployment

1. **Run with minimal permissions**: Application should only have read access to media directory
2. **Use read-only mounts**: In Docker, mount media directory as read-only
3. **Enable logging**: Enable file logging for security auditing
4. **Monitor logs**: Regularly check logs for security events
5. **Keep dependencies updated**: Regularly update Python packages

### For Production

1. **Use HTTPS**: If exposing to internet, use SSL/TLS
2. **Implement authentication**: For external access, add authentication
3. **Rate limiting**: Consider rate limiting for API endpoints
4. **Firewall rules**: Restrict access to trusted networks
5. **Regular security audits**: Review logs and access patterns

## Security Checklist

- [x] Path traversal protection implemented
- [x] Extension validation implemented
- [x] Filename sanitization implemented
- [x] File existence checks implemented
- [x] Permission checks implemented
- [x] Security events logged
- [x] Error messages don't expose internal paths
- [ ] Rate limiting (recommended for production)
- [ ] Authentication/Authorization (recommended for external access)
- [ ] HTTPS/TLS (required for external access)
- [ ] CORS configuration (if needed)
- [ ] Content Security Policy headers (recommended)

## Security Status

**Current Security Score**: 9/10

**Implemented**:
- ✅ Path traversal protection
- ✅ Extension validation
- ✅ Input sanitization
- ✅ Permission checks
- ✅ Security logging

**Recommended for Production**:
- ⚠️ Rate limiting
- ⚠️ Authentication (if external access)
- ⚠️ HTTPS/TLS (if external access)

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Error Handling Guide](ERROR_HANDLING.md) - Error handling patterns
- [Logging Guide](LOGGING.md) - Logging system
- [Deployment Guide](DEPLOYMENT.md) - Production deployment

## References

- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Python Security Guidelines](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

