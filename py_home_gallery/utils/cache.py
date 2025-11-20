"""
Cache utilities for Py Home Gallery.

This module provides simple caching mechanisms to improve performance
by reducing repeated filesystem operations.
"""

import time
import hashlib
import threading
from typing import Optional, Any, Dict, Callable
from functools import wraps
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)


class SimpleCache:
    """
    Simple in-memory cache with TTL (Time To Live) support.
    
    Thread-safe cache implementation for storing expensive operation results.
    
    Example:
        >>> cache = SimpleCache(ttl_seconds=300)
        >>> cache.set('key', 'value')
        >>> cache.get('key')
        'value'
    """
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize the cache.
        
        Args:
            ttl_seconds: Time to live for cached items in seconds (default: 300)
        """
        self._cache: Dict[str, tuple] = {}
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        logger.info(f"Cache initialized with TTL: {ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                age = time.time() - timestamp
                
                if age < self._ttl:
                    logger.debug(f"Cache HIT: {key} (age: {age:.2f}s)")
                    return value
                else:
                    logger.debug(f"Cache EXPIRED: {key} (age: {age:.2f}s)")
                    del self._cache[key]
            
            logger.debug(f"Cache MISS: {key}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            self._cache[key] = (value, time.time())
            logger.debug(f"Cache SET: {key} (total items: {len(self._cache)})")
    
    def invalidate(self, key: str) -> bool:
        """
        Remove a specific key from the cache.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            bool: True if key was found and removed, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache INVALIDATE: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache CLEARED: {count} items removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            dict: Cache statistics including size and items
        """
        with self._lock:
            return {
                'size': len(self._cache),
                'ttl': self._ttl,
                'items': list(self._cache.keys())
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired items from cache.
        
        Returns:
            int: Number of items removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp >= self._ttl
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
            
            return len(expired_keys)


# Global cache instances (initialized with default TTL, configured via setup_caches)
_directory_cache: Optional[SimpleCache] = None
_metadata_cache: Optional[SimpleCache] = None


def setup_caches(directory_ttl: int = 300, metadata_ttl: int = 600) -> None:
    """
    Initialize global cache instances with specified TTL values.
    
    Should be called once during application startup with config values.
    
    Args:
        directory_ttl: TTL for directory cache in seconds (default: 300)
        metadata_ttl: TTL for metadata cache in seconds (default: 600)
    """
    global _directory_cache, _metadata_cache
    
    _directory_cache = SimpleCache(ttl_seconds=directory_ttl)
    _metadata_cache = SimpleCache(ttl_seconds=metadata_ttl)
    
    logger.info(f"Caches initialized - Directory TTL: {directory_ttl}s, Metadata TTL: {metadata_ttl}s")


def get_directory_cache() -> SimpleCache:
    """
    Get the global directory cache instance.
    
    Returns:
        SimpleCache: Directory cache instance
    """
    global _directory_cache
    
    # Auto-initialize with defaults if not already set up
    if _directory_cache is None:
        logger.warning("Directory cache not initialized, using defaults")
        setup_caches()
    
    return _directory_cache


def get_metadata_cache() -> SimpleCache:
    """
    Get the global metadata cache instance.
    
    Returns:
        SimpleCache: Metadata cache instance
    """
    global _metadata_cache
    
    # Auto-initialize with defaults if not already set up
    if _metadata_cache is None:
        logger.warning("Metadata cache not initialized, using defaults")
        setup_caches()
    
    return _metadata_cache


def cached(ttl: int = 300, cache_instance: Optional[SimpleCache] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        cache_instance: Specific cache instance to use (default: creates new one)
        
    Example:
        >>> @cached(ttl=60)
        ... def expensive_operation(param):
        ...     # Expensive computation
        ...     return result
    """
    if cache_instance is None:
        cache_instance = SimpleCache(ttl_seconds=ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__module__}.{func.__name__}:{args}:{sorted(kwargs.items())}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            result = cache_instance.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            logger.debug(f"Executing {func.__name__} (cache miss)")
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result)
            
            return result
        
        # Add cache control methods to wrapper
        wrapper.cache = cache_instance
        wrapper.cache_clear = lambda: cache_instance.clear()
        wrapper.cache_stats = lambda: cache_instance.get_stats()
        
        return wrapper
    
    return decorator


def cache_key_for_directory(directory: str) -> str:
    """
    Generate a consistent cache key for a directory.
    
    Args:
        directory: Directory path
        
    Returns:
        str: Cache key
    """
    return f"dir:{hashlib.md5(directory.encode()).hexdigest()}"


def cache_key_for_file(filepath: str) -> str:
    """
    Generate a consistent cache key for a file.
    
    Args:
        filepath: File path
        
    Returns:
        str: Cache key
    """
    return f"file:{hashlib.md5(filepath.encode()).hexdigest()}"


def invalidate_directory_cache(directory: str) -> None:
    """
    Invalidate cache for a specific directory.
    
    Args:
        directory: Directory path to invalidate
    """
    cache_key = cache_key_for_directory(directory)
    _directory_cache.invalidate(cache_key)
    logger.info(f"Invalidated cache for directory: {directory}")

