"""
Background thumbnail generation worker for Py Home Gallery.

This module provides a worker thread pool for generating video thumbnails
in the background without blocking the main application thread.
"""

import threading
import queue
import time
from typing import Optional, Callable
from py_home_gallery.media.thumbnails import generate_video_thumbnail
from py_home_gallery.utils.logger import get_logger

logger = get_logger(__name__)


class ThumbnailWorker:
    """
    Background worker for generating video thumbnails.
    
    Uses a thread pool to generate thumbnails asynchronously,
    preventing the main thread from blocking during video processing.
    
    Example:
        >>> worker = ThumbnailWorker(num_threads=2)
        >>> worker.start()
        >>> worker.add_job('/path/to/video.mp4', '/path/to/thumb.png')
        >>> worker.wait_completion()
        >>> worker.stop()
    """
    
    def __init__(self, num_threads: int = 2, max_queue_size: int = 100):
        """
        Initialize the thumbnail worker.
        
        Args:
            num_threads: Number of worker threads (default: 2)
            max_queue_size: Maximum queue size (default: 100)
        """
        self.num_threads = num_threads
        self.job_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.threads = []
        self.running = False
        self.stats = {
            'jobs_completed': 0,
            'jobs_failed': 0,
            'jobs_pending': 0
        }
        self.stats_lock = threading.Lock()
        
        logger.info(f"ThumbnailWorker initialized with {num_threads} threads")
    
    def _worker(self) -> None:
        """Worker thread main loop."""
        thread_name = threading.current_thread().name
        logger.info(f"Worker thread {thread_name} started")
        
        while self.running:
            try:
                # Get job from queue with timeout
                job = self.job_queue.get(timeout=1)
                
                if job is None:  # Poison pill to stop thread
                    break
                
                video_path, thumbnail_path, callback = job
                
                logger.info(f"[{thread_name}] Processing: {video_path}")
                start_time = time.time()
                
                try:
                    # Generate thumbnail
                    success = generate_video_thumbnail(video_path, thumbnail_path)
                    duration = time.time() - start_time
                    
                    if success:
                        logger.info(f"[{thread_name}] Success: {video_path} ({duration:.2f}s)")
                        with self.stats_lock:
                            self.stats['jobs_completed'] += 1
                        
                        # Call callback if provided
                        if callback:
                            try:
                                callback(video_path, thumbnail_path, True)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                    else:
                        logger.warning(f"[{thread_name}] Failed: {video_path}")
                        with self.stats_lock:
                            self.stats['jobs_failed'] += 1
                        
                        if callback:
                            try:
                                callback(video_path, thumbnail_path, False)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                
                except Exception as e:
                    logger.error(f"[{thread_name}] Error processing {video_path}: {e}")
                    with self.stats_lock:
                        self.stats['jobs_failed'] += 1
                    
                    if callback:
                        try:
                            callback(video_path, thumbnail_path, False)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                
                finally:
                    self.job_queue.task_done()
                    with self.stats_lock:
                        self.stats['jobs_pending'] = self.job_queue.qsize()
            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker thread error: {e}")
        
        logger.info(f"Worker thread {thread_name} stopped")
    
    def start(self) -> None:
        """Start the worker threads."""
        if self.running:
            logger.warning("Worker already running")
            return
        
        self.running = True
        self.threads = []
        
        for i in range(self.num_threads):
            thread = threading.Thread(
                target=self._worker,
                name=f"ThumbnailWorker-{i+1}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        logger.info(f"Started {len(self.threads)} worker threads")
    
    def stop(self, wait: bool = True) -> None:
        """
        Stop the worker threads.
        
        Args:
            wait: Whether to wait for current jobs to complete (default: True)
        """
        if not self.running:
            return
        
        logger.info("Stopping thumbnail worker...")
        self.running = False
        
        # Send poison pills to stop threads
        for _ in range(self.num_threads):
            try:
                self.job_queue.put(None, block=False)
            except queue.Full:
                pass
        
        if wait:
            # Wait for all threads to finish
            for thread in self.threads:
                thread.join(timeout=5)
        
        self.threads = []
        logger.info("Thumbnail worker stopped")
    
    def add_job(self, video_path: str, thumbnail_path: str, 
                callback: Optional[Callable] = None) -> bool:
        """
        Add a thumbnail generation job to the queue.
        
        Args:
            video_path: Path to the video file
            thumbnail_path: Path where thumbnail should be saved
            callback: Optional callback function(video_path, thumb_path, success)
            
        Returns:
            bool: True if job was added, False if queue is full
        """
        if not self.running:
            logger.warning("Worker not running, cannot add job")
            return False
        
        try:
            self.job_queue.put((video_path, thumbnail_path, callback), block=False)
            with self.stats_lock:
                self.stats['jobs_pending'] = self.job_queue.qsize()
            logger.debug(f"Job added: {video_path}")
            return True
        except queue.Full:
            logger.warning(f"Job queue full, cannot add: {video_path}")
            return False
    
    def wait_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all jobs in the queue to complete.
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
            
        Returns:
            bool: True if all jobs completed, False if timeout
        """
        try:
            self.job_queue.join()
            logger.info("All thumbnail jobs completed")
            return True
        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get worker statistics.
        
        Returns:
            dict: Statistics including completed, failed, and pending jobs
        """
        with self.stats_lock:
            return {
                **self.stats,
                'running': self.running,
                'num_threads': self.num_threads,
                'queue_size': self.job_queue.qsize()
            }
    
    def is_busy(self) -> bool:
        """
        Check if worker has pending jobs.
        
        Returns:
            bool: True if there are pending jobs
        """
        return not self.job_queue.empty()
    
    def clear_queue(self) -> int:
        """
        Clear all pending jobs from the queue.
        
        Returns:
            int: Number of jobs cleared
        """
        count = 0
        try:
            while True:
                self.job_queue.get_nowait()
                self.job_queue.task_done()
                count += 1
        except queue.Empty:
            pass
        
        if count > 0:
            logger.info(f"Cleared {count} pending jobs from queue")
        
        return count


# Global worker instance
_global_worker: Optional[ThumbnailWorker] = None


def get_thumbnail_worker(num_threads: int = 2) -> ThumbnailWorker:
    """
    Get the global thumbnail worker instance.
    
    Creates and starts the worker if it doesn't exist.
    
    Args:
        num_threads: Number of worker threads (only used on first call)
        
    Returns:
        ThumbnailWorker: Global worker instance
    """
    global _global_worker
    
    if _global_worker is None:
        _global_worker = ThumbnailWorker(num_threads=num_threads)
        _global_worker.start()
        logger.info("Global thumbnail worker created and started")
    
    return _global_worker


def shutdown_thumbnail_worker() -> None:
    """Shutdown the global thumbnail worker."""
    global _global_worker
    
    if _global_worker is not None:
        _global_worker.stop(wait=True)
        _global_worker = None
        logger.info("Global thumbnail worker shut down")

