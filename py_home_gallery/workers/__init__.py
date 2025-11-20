"""
Background workers for Py Home Gallery.

This module contains background workers for handling
long-running or CPU-intensive tasks without blocking the main thread.
"""

from py_home_gallery.workers.thumbnail_worker import (
    ThumbnailWorker,
    get_thumbnail_worker,
    shutdown_thumbnail_worker
)
from py_home_gallery.workers.preload import preload_thumbnails, preload_all

__all__ = [
    'ThumbnailWorker',
    'get_thumbnail_worker',
    'shutdown_thumbnail_worker',
    'preload_thumbnails',
    'preload_all'
]

