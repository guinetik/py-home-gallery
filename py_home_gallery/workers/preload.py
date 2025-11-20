"""
Preload module for Py Home Gallery.

This module handles preloading of thumbnails and other resources
when the server starts.
"""

import os
import threading
from typing import List, Tuple
from py_home_gallery.media.scanner import scan_directory
from py_home_gallery.workers.thumbnail_worker import get_thumbnail_worker
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)


def preload_thumbnails(media_root: str, thumbnail_dir: str, num_threads: int = 2) -> None:
    """
    Preload thumbnails for all videos in the media directory.
    
    This function scans the media directory, identifies all video files,
    and queues them for thumbnail generation in the background.
    
    Args:
        media_root: Root media directory
        thumbnail_dir: Directory where thumbnails are stored
        num_threads: Number of worker threads to use
    """
    def preload_worker():
        """Background thread for preloading thumbnails."""
        try:
            logger.info("Starting thumbnail preload...")
            
            # Scan directory for all media files
            logger.info(f"Scanning directory: {media_root}")
            media_files = scan_directory(media_root, use_cache=False)
            
            # Filter video files
            video_files = [
                (path, thumb) for path, thumb in media_files
                if path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'))
            ]
            
            logger.info(f"Found {len(video_files)} video files")
            
            if not video_files:
                logger.info("No videos found, skipping thumbnail preload")
                return
            
            # Get the thumbnail worker
            worker = get_thumbnail_worker(num_threads=num_threads)
            
            # Prepare list of videos that need thumbnails
            videos_to_process = []
            skipped = 0

            for video_path, _ in video_files:
                # Construct full paths
                full_video_path = os.path.join(media_root, video_path)

                # Generate thumbnail filename
                safe_filename = video_path.replace('\\', '_').replace('/', '_')
                if len(safe_filename) > 200:
                    import hashlib
                    file_hash = hashlib.md5(safe_filename.encode()).hexdigest()
                    extension = os.path.splitext(safe_filename)[1]
                    safe_filename = f"{file_hash}{extension}"

                thumbnail_path = os.path.join(thumbnail_dir, f"{safe_filename}.png")

                # Check if thumbnail already exists
                if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
                    skipped += 1
                    logger.debug(f"Thumbnail exists, skipping: {video_path}")
                    continue

                # Check if video file exists
                if not os.path.exists(full_video_path):
                    logger.warning(f"Video file not found: {full_video_path}")
                    continue

                videos_to_process.append((full_video_path, thumbnail_path, video_path))

            logger.info(f"Found {len(videos_to_process)} videos needing thumbnails, {skipped} already exist")

            # Process in batches of 500
            batch_size = 500
            total_queued = 0

            for batch_num in range(0, len(videos_to_process), batch_size):
                batch = videos_to_process[batch_num:batch_num + batch_size]
                batch_count = len(batch)

                logger.info(f"Processing batch {batch_num // batch_size + 1}: {batch_count} videos")

                # Add batch to queue
                for full_video_path, thumbnail_path, video_path in batch:
                    success = worker.add_job(full_video_path, thumbnail_path, timeout=10.0)
                    if success:
                        total_queued += 1
                    else:
                        logger.warning(f"Failed to queue: {video_path}")

                # Wait for batch to complete before queuing next batch
                if batch_num + batch_size < len(videos_to_process):
                    logger.info(f"Waiting for batch to complete before queuing next batch...")
                    worker.wait_completion()
                    logger.info(f"Batch complete, continuing to next batch")

            logger.info(f"Thumbnail preload complete: {total_queued} total queued, {skipped} already exist")

            if total_queued > 0:
                logger.info(f"Background worker will generate {total_queued} thumbnails...")
        
        except Exception as e:
            logger.error(f"Error during thumbnail preload: {e}")
    
    # Start preload in background thread
    thread = threading.Thread(target=preload_worker, name="ThumbnailPreload", daemon=True)
    thread.start()
    logger.info("Thumbnail preload started in background")


def preload_all(media_root: str, thumbnail_dir: str, 
                worker_threads: int = 2, cache_enabled: bool = True) -> None:
    """
    Preload all resources (thumbnails, cache, etc.) when server starts.
    
    Args:
        media_root: Root media directory
        thumbnail_dir: Directory where thumbnails are stored
        worker_threads: Number of worker threads
        cache_enabled: Whether cache is enabled
    """
    logger.info("="*60)
    logger.info("PRELOADING RESOURCES")
    logger.info("="*60)
    
    # Preload directory cache if enabled
    if cache_enabled:
        try:
            logger.info("Warming up directory cache...")
            from py_home_gallery.media.scanner import scan_directory
            files = scan_directory(media_root, use_cache=True)
            logger.info(f"Cache warmed up: {len(files)} files indexed")
        except Exception as e:
            logger.error(f"Error warming up cache: {e}")
    
    # Preload thumbnails in background
    preload_thumbnails(media_root, thumbnail_dir, num_threads=worker_threads)
    
    logger.info("="*60)
    logger.info("PRELOAD INITIATED - Server ready for connections")
    logger.info("="*60)

