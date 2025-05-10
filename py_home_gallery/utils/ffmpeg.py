"""
FFmpeg validation utility for Py Home Gallery.

This module contains functions for checking if FFmpeg is installed
and accessible in the system PATH.
"""

import subprocess


def check_ffmpeg():
    """
    Check if FFmpeg is installed and accessible in PATH.
    Returns True if FFmpeg is available, False otherwise.
    """
    try:
        # Run ffmpeg command with version flag
        process = subprocess.Popen(
            ['ffmpeg', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        # Check if the command was successful
        if process.returncode == 0:
            return True
        return False
    except Exception:
        # If any exception occurs (like FileNotFoundError), FFmpeg is not installed
        return False
