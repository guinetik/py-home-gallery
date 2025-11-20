"""
Performance testing script for Py Home Gallery.

This script tests the performance improvements of caching and background workers.
"""

import time
import os
from py_home_gallery.media.scanner import scan_directory
from py_home_gallery.utils.cache import get_directory_cache
from py_home_gallery.workers.thumbnail_worker import ThumbnailWorker


def test_cache_performance(directory: str, iterations: int = 3):
    """
    Test cache performance by scanning directory multiple times.
    
    Args:
        directory: Directory to scan
        iterations: Number of iterations to test
    """
    print("\n" + "="*60)
    print("CACHE PERFORMANCE TEST")
    print("="*60)
    
    cache = get_directory_cache()
    
    # Clear cache to start fresh
    cache.clear()
    
    print(f"\nScanning directory: {directory}")
    print(f"Iterations: {iterations}")
    
    times_without_cache = []
    times_with_cache = []
    
    # Test WITHOUT cache
    print("\n--- Testing WITHOUT cache ---")
    for i in range(iterations):
        cache.clear()  # Clear cache before each run
        start = time.time()
        files = scan_directory(directory, use_cache=False)
        duration = time.time() - start
        times_without_cache.append(duration)
        print(f"  Run {i+1}: {duration:.3f}s ({len(files)} files)")
    
    # Test WITH cache
    print("\n--- Testing WITH cache ---")
    cache.clear()  # Clear cache once at the start
    for i in range(iterations):
        start = time.time()
        files = scan_directory(directory, use_cache=True)
        duration = time.time() - start
        times_with_cache.append(duration)
        status = "CACHED" if i > 0 else "FIRST RUN"
        print(f"  Run {i+1}: {duration:.3f}s ({len(files)} files) [{status}]")
    
    # Calculate improvements
    avg_without = sum(times_without_cache) / len(times_without_cache)
    avg_with = sum(times_with_cache[1:]) / len(times_with_cache[1:]) if len(times_with_cache) > 1 else times_with_cache[0]
    improvement = ((avg_without - avg_with) / avg_without * 100) if avg_without > 0 else 0
    
    print("\n--- RESULTS ---")
    print(f"  Average WITHOUT cache: {avg_without:.3f}s")
    print(f"  Average WITH cache (cached runs): {avg_with:.3f}s")
    print(f"  Improvement: {improvement:.1f}% faster")
    print(f"  Speedup: {avg_without/avg_with:.1f}x" if avg_with > 0 else "N/A")
    
    # Cache stats
    stats = cache.get_stats()
    print(f"\n  Cache stats: {stats['size']} items, TTL: {stats['ttl']}s")


def test_worker_performance(video_files: list, num_threads: int = 2):
    """
    Test background worker performance for thumbnail generation.
    
    Args:
        video_files: List of video file paths
        num_threads: Number of worker threads
    """
    print("\n" + "="*60)
    print("BACKGROUND WORKER TEST")
    print("="*60)
    
    if not video_files:
        print("\n  No video files found to test")
        return
    
    print(f"\nVideo files to process: {len(video_files)}")
    print(f"Worker threads: {num_threads}")
    
    # Test synchronous (no worker)
    print("\n--- Testing SYNCHRONOUS generation ---")
    from py_home_gallery.media.thumbnails import generate_video_thumbnail
    
    sync_times = []
    for i, video in enumerate(video_files[:3]):  # Test first 3
        thumb_path = f"/tmp/thumb_sync_{i}.png"
        start = time.time()
        success = generate_video_thumbnail(video, thumb_path)
        duration = time.time() - start
        sync_times.append(duration)
        print(f"  Video {i+1}: {duration:.3f}s {'✓' if success else '✗'}")
    
    # Test with worker
    print("\n--- Testing BACKGROUND WORKER generation ---")
    worker = ThumbnailWorker(num_threads=num_threads)
    worker.start()
    
    start = time.time()
    for i, video in enumerate(video_files[:3]):
        thumb_path = f"/tmp/thumb_worker_{i}.png"
        worker.add_job(video, thumb_path)
    
    # Wait for completion
    worker.wait_completion()
    total_duration = time.time() - start
    
    worker.stop()
    
    stats = worker.get_stats()
    print(f"\n  Total time (parallel): {total_duration:.3f}s")
    print(f"  Jobs completed: {stats['jobs_completed']}")
    print(f"  Jobs failed: {stats['jobs_failed']}")
    
    if sync_times:
        sync_total = sum(sync_times)
        speedup = sync_total / total_duration if total_duration > 0 else 0
        print(f"\n  Synchronous total: {sync_total:.3f}s")
        print(f"  Improvement: {((sync_total - total_duration) / sync_total * 100):.1f}% faster")
        print(f"  Speedup: {speedup:.1f}x")


def main():
    """Run all performance tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PERFORMANCE TEST SUITE" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test cache with sample gallery
    test_directory = "./samplegallery"
    if os.path.exists(test_directory):
        test_cache_performance(test_directory, iterations=3)
    else:
        print(f"\n⚠️  Directory not found: {test_directory}")
        print("  Please provide a valid directory path")
    
    # Test worker with video files
    if os.path.exists(test_directory):
        video_files = [
            os.path.join(test_directory, f)
            for f in os.listdir(test_directory)
            if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
        ]
        
        if video_files:
            test_worker_performance(video_files, num_threads=2)
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

