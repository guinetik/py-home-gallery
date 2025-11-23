# Development Guide - Py Home Gallery

## Overview

This guide is for developers who want to contribute to Py Home Gallery. It covers development setup, code structure, conventions, and best practices.

## Development Setup

### Prerequisites

- Python 3.10+
- FFmpeg installed and in PATH
- Git

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/guinetik/py-home-gallery.git
   cd py-home-gallery
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run in development mode**:
   ```bash
   python run.py --media-dir ./samplegallery --log-level DEBUG --no-cache
   ```

## Code Structure

### Package Organization

```
py_home_gallery/
├── app.py              # Flask application factory
├── config.py           # Configuration management
├── media/              # Media handling
│   ├── scanner.py      # Directory scanning
│   ├── thumbnails.py   # Thumbnail generation
│   └── utils.py        # Media utilities
├── routes/             # Flask route blueprints
│   ├── gallery.py      # Gallery routes
│   ├── browse.py       # Browse routes
│   ├── infinite.py     # Infinite scroll routes
│   ├── media.py        # Media serving routes
│   └── metadata.py     # Metadata API routes
├── utils/              # Utility modules
│   ├── cache.py        # Caching system
│   ├── logger.py       # Logging system
│   ├── security.py     # Security utilities
│   └── pagination.py   # Pagination utilities
└── workers/            # Background workers
    ├── thumbnail_worker.py  # Thumbnail worker
    └── preload.py      # Cache preloading
```

See [Architecture Guide](ARCHITECTURE.md) for detailed architecture documentation.

## Code Conventions

### Python Style

Follow PEP 8 style guidelines:

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Use docstrings for all functions and classes

### Import Organization

```python
# Standard library imports
import os
from typing import List, Optional

# Third-party imports
from flask import Blueprint, render_template
from PIL import Image

# Local imports
from py_home_gallery.utils.logger import get_logger
from py_home_gallery.utils.security import get_safe_path
```

### Function Documentation

Use docstrings following Google style:

```python
def scan_directory(directory: str, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Recursively scans a directory for media files.
    
    Args:
        directory: Path to the directory to scan
        use_cache: Whether to use cache (default: True)
        
    Returns:
        List[Dict[str, Any]]: List of media file dictionaries
        
    Raises:
        PermissionError: If directory is not accessible
    """
    ...
```

## Type Hints

All functions should have type hints for better code quality and IDE support.

### Basic Types

```python
def process_file(filename: str) -> bool:
    """Process a file and return success status."""
    ...

def get_count() -> int:
    """Get the count of items."""
    ...

def get_name() -> Optional[str]:
    """Get name or None if not available."""
    ...
```

### Collection Types

```python
from typing import List, Dict, Tuple, Optional

def get_files() -> List[str]:
    """Get list of file paths."""
    ...

def get_metadata() -> Dict[str, Any]:
    """Get metadata dictionary."""
    ...

def scan_directory() -> List[Tuple[str, str]]:
    """Scan directory and return list of tuples."""
    ...
```

### Optional Types

```python
from typing import Optional

def find_file(name: str) -> Optional[str]:
    """Find file by name, return path or None."""
    ...
```

### Union Types

```python
from typing import Union

def process_data(data: Union[str, List[str]]) -> List[str]:
    """Process string or list of strings."""
    ...
```

### Type Variables (Generics)

```python
from typing import TypeVar, List

T = TypeVar('T')

def first_item(items: List[T]) -> T:
    """Return first item from list."""
    return items[0]
```

### Function Parameters

```python
def create_thumbnail(
    path: str,
    width: int = 300,
    height: int = 200,
    quality: int = 85
) -> bool:
    """Create thumbnail with optional parameters."""
    ...
```

### Type Checking

Use `mypy` for static type checking:

```bash
# Install mypy
pip install mypy

# Check types
mypy py_home_gallery/

# With configuration
mypy --config-file mypy.ini py_home_gallery/
```

### Type Hint Best Practices

1. **Always annotate function parameters and return types**
2. **Use `Optional` for values that can be None**
3. **Be specific with collection types** (`List[str]` not `list`)
4. **Use type aliases for complex types**
5. **Document complex types in docstrings**

## Error Handling

Follow consistent error handling patterns:

```python
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

def process_file(file_path: str) -> bool:
    """Process file with error handling."""
    try:
        # Validate input
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return False
        
        # Process file
        result = do_processing(file_path)
        return True
    
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}", exc_info=True)
        return False
```

See [Error Handling Guide](ERROR_HANDLING.md) for detailed patterns.

## Logging

Always use the centralized logger:

```python
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

See [Logging Guide](LOGGING.md) for detailed logging practices.

## Security

Always use security utilities for file access:

```python
from py_home_gallery.utils.security import get_safe_path, validate_media_extension

# Validate extension
if not validate_media_extension(filename):
    abort(400, description="Invalid file type")

# Validate path
file_path = get_safe_path(media_root, filename)
if not file_path:
    abort(403, description="Access denied")
```

See [Security Guide](SECURITY.md) for security best practices.

## Adding New Features

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature-name
```

### 2. Implement Feature

- Follow code conventions
- Add type hints
- Add error handling
- Add logging
- Add security checks

### 3. Update Documentation

- Update relevant documentation files
- Add examples if needed
- Update API documentation if adding endpoints

### 4. Test Feature

- Test manually
- Test edge cases
- Test error conditions

### 5. Submit Pull Request

- Write clear commit messages
- Reference issues if applicable
- Describe changes in PR description

## Adding New Routes

### 1. Create Route File (if new module)

```python
"""
Route handler for new feature.
"""

from flask import Blueprint, render_template
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint('feature', __name__)

@bp.route('/feature')
def feature():
    """Feature route handler."""
    return render_template('feature.html')
```

### 2. Register Blueprint

In `py_home_gallery/routes/__init__.py`:

```python
from py_home_gallery.routes import feature

def register_routes(app):
    app.register_blueprint(feature.bp)
    # ... other blueprints
```

### 3. Add Template (if needed)

Create template in `templates/feature.html`

### 4. Update Documentation

- Add route to [API Reference](API.md)
- Update [Architecture Guide](ARCHITECTURE.md) if needed

## Testing

### Manual Testing

1. **Test basic functionality**
2. **Test error conditions**
3. **Test edge cases**
4. **Test with different file types**
5. **Test with large directories**

### Test Checklist

- [ ] Feature works as expected
- [ ] Error handling works correctly
- [ ] Security checks are in place
- [ ] Logging is appropriate
- [ ] Type hints are correct
- [ ] Documentation is updated

## Code Review Guidelines

### What to Review

1. **Code quality**: Follows conventions, readable
2. **Type hints**: All functions have type hints
3. **Error handling**: Proper error handling and logging
4. **Security**: Security checks are in place
5. **Documentation**: Code is documented
6. **Performance**: No obvious performance issues

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Type hints are present and correct
- [ ] Error handling is appropriate
- [ ] Security checks are in place
- [ ] Logging is appropriate
- [ ] Documentation is updated
- [ ] No obvious bugs

## Debugging

### Enable Debug Logging

```bash
python run.py --log-level DEBUG
```

### View Logs

```bash
# Real-time logs
tail -f logs/app.log

# Filter by module
grep "scanner" logs/app.log

# Filter by level
grep "ERROR" logs/app.log
```

### Debug in Code

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add debug statements
logger.debug(f"Variable value: {variable}")
```

## Git Workflow

### Commit Messages

Use clear, descriptive commit messages:

```
Add thumbnail generation for videos

- Implement video thumbnail generation using moviepy
- Add error handling for large files
- Add logging for thumbnail operations
```

### Branch Naming

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation updates
- `refactor/refactoring-description` - Code refactoring

### Pull Request Process

1. Create feature branch
2. Make changes
3. Test changes
4. Update documentation
5. Create pull request
6. Address review comments
7. Merge when approved

## Performance Considerations

### Caching

Use cache for expensive operations:

```python
from py_home_gallery.utils.cache import cached

@cached(ttl=300)
def expensive_operation(param):
    # Expensive computation
    return result
```

### Lazy Loading

Load data only when needed:

```python
# Don't load dimensions for all files
files = scan_directory(directory, include_dimensions=False)

# Load dimensions only for displayed items
for item in paginated_items:
    add_dimensions(item)
```

### Background Workers

Use workers for long-running operations:

```python
from py_home_gallery.workers.thumbnail_worker import get_thumbnail_worker

worker = get_thumbnail_worker()
worker.add_job(video_path, thumbnail_path)
```

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Error Handling Guide](ERROR_HANDLING.md) - Error handling patterns
- [Logging Guide](LOGGING.md) - Logging system
- [Security Guide](SECURITY.md) - Security best practices
- [API Reference](API.md) - API endpoints

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

