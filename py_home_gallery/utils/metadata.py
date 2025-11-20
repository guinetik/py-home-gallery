"""
Metadata extraction utility for images and videos.

This module provides functions to extract EXIF data, file information,
and other metadata from media files.
"""

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from typing import Dict, Any, Optional


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic file information.

    Args:
        file_path: Path to the media file

    Returns:
        Dictionary containing file information
    """
    try:
        stats = os.stat(file_path)
        return {
            'filename': os.path.basename(file_path),
            'size': stats.st_size,
            'size_mb': round(stats.st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
        }
    except Exception as e:
        return {
            'filename': os.path.basename(file_path),
            'error': str(e)
        }


def _convert_to_serializable(obj):
    """
    Convert PIL EXIF objects to JSON-serializable types.

    Args:
        obj: The object to convert

    Returns:
        JSON-serializable version of the object
    """
    # Handle None
    if obj is None:
        return None

    # Handle PIL's IFDRational (fraction) type
    if hasattr(obj, 'numerator') and hasattr(obj, 'denominator'):
        try:
            if obj.denominator == 0:
                return 0
            return float(obj.numerator) / float(obj.denominator)
        except:
            return str(obj)

    # Handle bytes
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8', errors='ignore')
        except:
            return None

    # Handle tuples (convert to list)
    if isinstance(obj, tuple):
        return [_convert_to_serializable(item) for item in obj]

    # Handle lists
    if isinstance(obj, list):
        return [_convert_to_serializable(item) for item in obj]

    # Handle dictionaries (sort keys to ensure consistent ordering)
    if isinstance(obj, dict):
        return {str(k): _convert_to_serializable(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}

    # Handle basic JSON-serializable types
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # For anything else, try to convert to string
    try:
        # Check if it's JSON serializable
        import json
        json.dumps(obj)
        return obj
    except:
        return str(obj)


def get_image_exif(file_path: str) -> Dict[str, Any]:
    """
    Extract EXIF data from an image file.

    Args:
        file_path: Path to the image file

    Returns:
        Dictionary containing EXIF data
    """
    exif_data = {}

    try:
        image = Image.open(file_path)

        # Get basic image info
        exif_data['format'] = image.format
        exif_data['mode'] = image.mode
        exif_data['width'] = image.width
        exif_data['height'] = image.height
        exif_data['dimensions'] = f"{image.width}x{image.height}"

        # Get EXIF data if available
        exif = image.getexif()

        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)

                # Skip binary data
                if isinstance(value, bytes):
                    continue

                # Convert to JSON-serializable format
                value = _convert_to_serializable(value)

                # Skip very long string values
                if isinstance(value, str) and len(value) > 200:
                    value = value[:200] + '...'

                exif_data[tag] = value

            # Parse GPS info if available
            gps_info = exif.get(0x8825)  # GPSInfo tag
            if gps_info:
                gps_data = {}
                for key in gps_info.keys():
                    decode = GPSTAGS.get(key, key)
                    gps_data[decode] = _convert_to_serializable(gps_info[key])
                exif_data['GPSInfo'] = gps_data

    except Exception as e:
        exif_data['error'] = str(e)

    return exif_data


def get_video_info(file_path: str) -> Dict[str, Any]:
    """
    Extract basic video file information.

    Args:
        file_path: Path to the video file

    Returns:
        Dictionary containing video information
    """
    video_info = {}

    try:
        # Try to get video info using opencv if available
        import cv2
        cap = cv2.VideoCapture(file_path)

        if cap.isOpened():
            video_info['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_info['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_info['dimensions'] = f"{video_info['width']}x{video_info['height']}"
            video_info['fps'] = round(cap.get(cv2.CAP_PROP_FPS), 2)
            video_info['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if video_info['fps'] > 0:
                duration = video_info['frame_count'] / video_info['fps']
                video_info['duration'] = round(duration, 2)
                video_info['duration_formatted'] = format_duration(duration)

            cap.release()
    except Exception as e:
        video_info['error'] = str(e)

    return video_info


def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_media_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive metadata for a media file.

    Args:
        file_path: Path to the media file

    Returns:
        Dictionary containing all available metadata
    """
    if not os.path.exists(file_path):
        return {'error': 'File not found'}

    metadata = {}

    # Get basic file info
    metadata['file'] = get_file_info(file_path)

    # Determine file type and get appropriate metadata
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        metadata['type'] = 'image'
        metadata['exif'] = get_image_exif(file_path)
    elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
        metadata['type'] = 'video'
        metadata['video'] = get_video_info(file_path)
    else:
        metadata['type'] = 'unknown'

    return metadata


def format_metadata_for_display(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format metadata for clean display in UI.

    Args:
        metadata: Raw metadata dictionary

    Returns:
        Formatted metadata dictionary
    """
    formatted = {
        'file_info': {},
        'technical': {},
        'camera': {},
        'location': {}
    }

    try:
        # File information
        if 'file' in metadata:
            file_data = metadata['file']
            formatted['file_info'] = {
                'Filename': file_data.get('filename', 'N/A'),
                'Size': f"{file_data.get('size_mb', 0)} MB",
                'Modified': file_data.get('modified', 'N/A'),
            }
    except Exception as e:
        print(f"Error formatting file info: {e}")

    try:
        # Technical information
        if 'exif' in metadata:
            exif = metadata['exif']

            # Basic dimensions
            if 'dimensions' in exif:
                formatted['technical']['Dimensions'] = exif['dimensions']

            # Camera settings
            camera_fields = {
                'Make': 'Make',
                'Model': 'Model',
                'LensModel': 'Lens',
                'FNumber': 'Aperture',
                'ExposureTime': 'Shutter Speed',
                'ISOSpeedRatings': 'ISO',
                'FocalLength': 'Focal Length',
                'DateTime': 'Date Taken',
            }

            for exif_key, display_name in camera_fields.items():
                try:
                    if exif_key in exif:
                        value = exif[exif_key]

                        # Format specific fields
                        if exif_key == 'FNumber' and isinstance(value, (int, float)):
                            value = f"f/{value}"
                        elif exif_key == 'ExposureTime' and isinstance(value, (int, float)):
                            if value < 1 and value > 0:
                                value = f"1/{int(1/value)}s"
                            else:
                                value = f"{value}s"
                        elif exif_key == 'FocalLength' and isinstance(value, (int, float)):
                            value = f"{value}mm"
                        elif exif_key == 'ISOSpeedRatings':
                            # ISO can be a list or single value
                            if isinstance(value, list):
                                value = value[0] if value else 'N/A'

                        formatted['camera'][display_name] = str(value)
                except Exception as e:
                    print(f"Error formatting {exif_key} (value={exif.get(exif_key)}): {e}")
    except Exception as e:
        print(f"Error formatting EXIF data: {e}")

    if 'video' in metadata:
        video = metadata['video']
        if 'dimensions' in video:
            formatted['technical']['Dimensions'] = video['dimensions']
        if 'fps' in video:
            formatted['technical']['Frame Rate'] = f"{video['fps']} fps"
        if 'duration_formatted' in video:
            formatted['technical']['Duration'] = video['duration_formatted']

    # Remove empty sections
    formatted = {k: v for k, v in formatted.items() if v}

    return formatted
