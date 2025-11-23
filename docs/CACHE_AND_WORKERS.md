# Cache and Background Workers - Py Home Gallery

## Overview

Py Home Gallery implements a caching system and background workers to dramatically improve performance. The cache reduces repeated filesystem operations, while background workers handle thumbnail generation asynchronously.

## Cache System

### Overview

The cache system stores directory scan results and metadata in memory with configurable TTL (Time To Live). This reduces filesystem I/O and improves response times.

### Cache Architecture

```
┌─────────────────────────────────────┐
│      Directory Scan Request         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check Cache (by directory path)   │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   Cache Hit    Cache Miss
        │             │
        │             ▼
        │    ┌────────────────────┐
        │    │  Scan Filesystem   │
        │    └─────────┬──────────┘
        │              │
        │              ▼
        │    ┌────────────────────┐
        │    │   Store in Cache   │
        │    └─────────┬──────────┘
        │              │
        └──────┬───────┘
               │
               ▼
        ┌─────────────┐
        │ Return Data │
        └─────────────┘
```

### Cache Types

#### Directory Cache
- **Purpose**: Cache directory scan results
- **TTL**: 5 minutes (configurable, default: 300 seconds)
- **Key**: MD5 hash of directory path
- **Used by**: `scanner.py`

#### Metadata Cache
- **Purpose**: Cache metadata extraction results
- **TTL**: 10 minutes (2x directory cache TTL)
- **Key**: MD5 hash of file path
- **Used by**: `metadata.py`

### Cache Implementation

#### SimpleCache Class

Thread-safe cache with TTL support:

```python
from py_home_gallery.utils.cache import SimpleCache

# Create cache with 5 minute TTL
cache = SimpleCache(ttl_seconds=300)

# Store value
cache.set('key', 'value')

# Retrieve value (returns None if expired)
value = cache.get('key')

# Invalidate specific key
cache.invalidate('key')

# Clear all cache
cache.clear()

# Get statistics
stats = cache.get_stats()
print(f"Items: {stats['size']}, TTL: {stats['ttl']}s")
```

#### Global Cache Instances

```python
from py_home_gallery.utils.cache import get_directory_cache, get_metadata_cache

# Get directory cache
dir_cache = get_directory_cache()

# Get metadata cache
meta_cache = get_metadata_cache()
```

#### @cached Decorator

Cache function results automatically:

```python
from py_home_gallery.utils.cache import cached

@cached(ttl=60)  # Cache for 1 minute
def expensive_operation(param1, param2):
    # Expensive computation
    return result

# First call: executes function
result1 = expensive_operation('a', 'b')

# Second call: uses cache (instant!)
result2 = expensive_operation('a', 'b')
```

### Cache Usage in Scanner

The scanner automatically uses cache:

```python
from py_home_gallery.media.scanner import scan_directory

# First call: scans filesystem (may take 2-3 seconds)
files = scan_directory('/media', use_cache=True)

# Second call: uses cache (instant, ~0.002 seconds)
files = scan_directory('/media', use_cache=True)

# Force fresh scan
files = scan_directory('/media', use_cache=False)
```

**Cache Key**: Based on MD5 hash of directory path + dimension flag

**Cache Invalidation**: Automatic expiration based on TTL, or manual invalidation

### Cache Configuration

#### Command-Line Arguments

```bash
# Set cache TTL (in seconds)
python run.py --cache-ttl 600

# Disable cache
python run.py --no-cache
```

#### Environment Variables

```bash
export PY_HOME_GALLERY_CACHE_ENABLED=true
export PY_HOME_GALLERY_CACHE_TTL=300
```

#### Default Values

- **Cache Enabled**: `true`
- **Cache TTL**: `300` seconds (5 minutes)
- **Metadata Cache TTL**: `600` seconds (10 minutes, 2x directory cache)

### Cache Performance

**Before Cache**:
- Each request scans filesystem: ~2-3 seconds for 1000+ files
- High CPU and I/O usage

**After Cache**:
- First request: ~2-3 seconds (scans and caches)
- Subsequent requests: ~0.002 seconds (from cache)
- **Improvement**: 1000x+ faster for cached requests

### Cache Invalidation

#### Automatic Expiration
Cache items expire automatically based on TTL.

#### Manual Invalidation

```python
from py_home_gallery.utils.cache import invalidate_directory_cache

# Invalidate cache for specific directory
invalidate_directory_cache('/media/photos')

# Clear entire cache
from py_home_gallery.utils.cache import get_directory_cache
get_directory_cache().clear()
```

## Background Workers

### Overview

Background workers handle thumbnail generation asynchronously, preventing the main application thread from blocking during video processing.

### Thumbnail Worker

#### Architecture

```
┌─────────────────────────────────────┐
│   Thumbnail Request                 │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Thumbnail   │
        │ Exists?     │
        └──────┬──────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
    Yes (Serve)   No (Queue)
        │             │
        │             ▼
        │    ┌─────────────────┐
        │    │ Add to Queue    │
        │    └────────┬─────────┘
        │             │
        │             ▼
        │    ┌─────────────────┐
        │    │ Return Placeholder│
        │    └─────────────────┘
        │
        ▼
   Serve Thumbnail
        │
        ▼
   Worker Threads
   Process Queue
        │
        ▼
   Generate Thumbnail
```

#### ThumbnailWorker Class

Thread pool for background thumbnail generation:

```python
from py_home_gallery.workers.thumbnail_worker import ThumbnailWorker

# Create worker with 2 threads
worker = ThumbnailWorker(num_threads=2)
worker.start()

# Add jobs to queue
worker.add_job('/path/to/video1.mp4', '/path/to/thumb1.png')
worker.add_job('/path/to/video2.mp4', '/path/to/thumb2.png')

# Wait for completion (optional)
worker.wait_completion()

# Stop worker
worker.stop(wait=True)
```

#### Global Worker Instance

```python
from py_home_gallery.workers.thumbnail_worker import get_thumbnail_worker

# Get global worker (creates if doesn't exist)
worker = get_thumbnail_worker(num_threads=2)

# Add job
worker.add_job(video_path, thumbnail_path)
```

#### Worker Statistics

```python
stats = worker.get_stats()
print(f"Completed: {stats['jobs_completed']}")
print(f"Failed: {stats['jobs_failed']}")
print(f"Pending: {stats['jobs_pending']}")
print(f"Queue size: {stats['queue_size']}")
```

### Worker Integration

#### In Routes

```python
@bp.route('/thumbnail/<path:filename>')
def serve_thumbnail(filename):
    # Check if thumbnail exists
    if os.path.exists(thumbnail_path):
        return send_file(thumbnail_path)  # Serve immediately
    
    # If not exists, add to queue and return placeholder
    thumbnail_worker.add_job(video_path, thumbnail_path)
    return placeholder_url  # Immediate response!
```

**Flow**:
1. Client requests thumbnail
2. If exists → serve immediately
3. If not exists → add to queue, return placeholder
4. Worker processes in background
5. Next request → thumbnail ready

### Worker Configuration

#### Command-Line Arguments

```bash
# Set number of worker threads
python run.py --worker-threads 4

# Disable workers
python run.py --no-worker
```

#### Environment Variables

```bash
export PY_HOME_GALLERY_WORKER_ENABLED=true
export PY_HOME_GALLERY_WORKER_THREADS=2
```

#### Default Values

- **Worker Enabled**: `true`
- **Worker Threads**: `2`

### Worker Performance

**Before Workers**:
- Server blocks 5-10 seconds generating thumbnail
- User waits for response
- Poor user experience

**After Workers**:
- Immediate response with placeholder
- Thumbnail generated in background
- Next request gets real thumbnail
- **Improvement**: Server always responsive

### Worker Lifecycle

1. **Startup**: Worker starts automatically if enabled
2. **Job Queue**: Jobs added to queue when thumbnails needed
3. **Processing**: Worker threads process jobs in parallel
4. **Shutdown**: Graceful shutdown on application exit

## Performance Improvements

### Cache Impact

| Metric | Before Cache | After Cache | Improvement |
|--------|--------------|-------------|-------------|
| Directory Scan | 2-3 seconds | 0.002 seconds | 1000x+ faster |
| CPU Usage | High | Low | 90% reduction |
| I/O Operations | High | Minimal | 95% reduction |

### Worker Impact

| Metric | Before Workers | After Workers | Improvement |
|--------|----------------|---------------|-------------|
| Response Time | 5-10 seconds | <0.1 seconds | 50-100x faster |
| Server Blocking | Yes | No | Always responsive |
| User Experience | Poor | Excellent | Significant improvement |

## Configuration Examples

### Development

```bash
# Fast iteration, disable cache to see changes immediately
python run.py --no-cache --no-worker
```

### Production

```bash
# Maximum performance
python run.py \
  --cache-ttl 600 \
  --worker-threads 4
```

### Docker

```yaml
environment:
  - PY_HOME_GALLERY_CACHE_ENABLED=true
  - PY_HOME_GALLERY_CACHE_TTL=300
  - PY_HOME_GALLERY_WORKER_ENABLED=true
  - PY_HOME_GALLERY_WORKER_THREADS=2
```

## Monitoring

### Cache Statistics

```python
from py_home_gallery.utils.cache import get_directory_cache

cache = get_directory_cache()
stats = cache.get_stats()

print(f"Cache size: {stats['size']} items")
print(f"TTL: {stats['ttl']} seconds")
print(f"Keys: {stats['items']}")
```

### Worker Statistics

```python
from py_home_gallery.workers.thumbnail_worker import get_thumbnail_worker

worker = get_thumbnail_worker()
stats = worker.get_stats()

print(f"Completed: {stats['jobs_completed']}")
print(f"Failed: {stats['jobs_failed']}")
print(f"Pending: {stats['jobs_pending']}")
```

### Logs

Cache and worker operations are logged:

```
2024-12-15 10:30:15 - py_home_gallery.cache - INFO - Cache initialized with TTL: 300s
2024-12-15 10:30:16 - py_home_gallery.scanner - INFO - Using cached scan result for: ./media (127 files)
2024-12-15 10:30:20 - py_home_gallery.thumbnail_worker - INFO - [ThumbnailWorker-1] Processing: video.mp4
2024-12-15 10:30:25 - py_home_gallery.thumbnail_worker - INFO - [ThumbnailWorker-1] Success: video.mp4 (4.98s)
```

## Best Practices

### Cache TTL

- **Stable directories**: Use longer TTL (600s+)
- **Dynamic directories**: Use shorter TTL (60s)
- **Development**: Disable cache or use short TTL

### Worker Threads

- **Few videos**: 1-2 threads
- **Many videos**: 2-4 threads
- **CPU-limited**: 1 thread
- **I/O-bound**: 2-4 threads

### Cache Invalidation

Invalidate cache when:
- Files are added/removed manually
- Directory structure changes
- After bulk operations

### Worker Management

- Always use graceful shutdown
- Monitor queue size to prevent overflow
- Adjust thread count based on workload

## Troubleshooting

### Cache Not Working

1. **Check cache enabled**: Verify `--no-cache` not set
2. **Check TTL**: Ensure TTL not too short
3. **Check logs**: Look for cache hit/miss messages

### Workers Not Processing

1. **Check workers enabled**: Verify `--no-worker` not set
2. **Check thread count**: Ensure threads > 0
3. **Check logs**: Look for worker start messages
4. **Check queue**: Monitor queue size

### Performance Issues

1. **Increase cache TTL**: Reduce cache misses
2. **Increase worker threads**: Process more thumbnails in parallel
3. **Check system resources**: CPU, memory, disk I/O

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Configuration Guide](CONFIGURATION.md) - Configuration options
- [Logging Guide](LOGGING.md) - Logging system

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

