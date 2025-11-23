"""
Gallery route handlers for Py Home Gallery.

This module contains route handlers for the main gallery views,
including default, random, and newest-first sorting.
"""

from flask import Blueprint, render_template, request, current_app
from py_home_gallery.media.scanner import list_subfolders, validate_and_get_folder_path, get_sorted_files
from py_home_gallery.media.dimension_helper import add_dimensions_to_items
from py_home_gallery.utils.pagination import paginate_items
from py_home_gallery.media.utils import is_image, is_video

# Create a blueprint for gallery routes
bp = Blueprint('gallery', __name__)


def handle_gallery(folder=None, sort_by="default", media_type=None):
    """
    Unified handler for gallery endpoints.
    - folder: Subfolder to filter files.
    - sort_by: Sorting method ('default', 'random', 'new').
    - media_type: Filter by 'images', 'videos', or None (all)
    """
    media_root = current_app.config['MEDIA_ROOT']
    items_per_page = current_app.config['ITEMS_PER_PAGE']
    placeholder_url = current_app.config['PLACEHOLDER_URL']
    
    # Validate the folder path
    folder_path = validate_and_get_folder_path(media_root, folder)
    if not folder_path:
        return "Folder not found", 404
    
    # Get sorted files from the specified folder (without dimensions for speed)
    # Dimensions will be added later only for paginated items
    try:
        media = get_sorted_files(media_root, folder_path, sort_by=sort_by, include_dimensions=False)
        print(f"Retrieved {len(media)} media files from {folder_path}")
    except Exception as e:
        print(f"Error getting files: {e}")
        return f"Error retrieving files: {str(e)}", 500
    
    # Filter by media type if specified
    if media_type == 'images':
        media = [item for item in media if is_image(item['path'])]
    elif media_type == 'videos':
        media = [item for item in media if is_video(item['path'])]

    # Paginate the files
    page = int(request.args.get('page', 1))
    paginated_media, total_pages = paginate_items(media, page, items_per_page)

    # Extract real dimensions for paginated items only
    thumbnail_dir = current_app.config['THUMBNAIL_DIR']
    add_dimensions_to_items(paginated_media, media_root, thumbnail_dir)

    # List all subfolders for dropdown
    folders = list_subfolders(media_root)

    # Count different media types for the UI
    image_count = len([item for item in media if is_image(item['path'])])
    video_count = len([item for item in media if is_video(item['path'])])
    total_count = len(media)
    
    print(f"Media stats - Total: {total_count}, Images: {image_count}, Videos: {video_count}")

    # Render the template
    return render_template(
        'gallery.html',
        media_files=paginated_media,
        page=page,
        total_pages=total_pages,
        placeholder=placeholder_url,
        folders=folders,
        current_folder=folder,
        media_type=media_type,
        image_count=image_count,
        video_count=video_count,
        total_count=total_count
    )


@bp.route('/')
def index():
    """
    Index page with buttons to navigate to different gallery views.
    """
    return render_template('index.html')


@bp.route('/gallery')
def gallery():
    """
    Default gallery view with optional folder filtering and pagination.
    """
    folder = request.args.get('folder')  # Get folder query parameter
    media_type = request.args.get('display')  # Get display filter parameter
    return handle_gallery(folder=folder, sort_by="default", media_type=media_type)


@bp.route('/random')
def random_gallery():
    """
    Randomized gallery view with shuffle button (no pagination).
    Shows a fixed number of random items that can be reshuffled.
    """
    import time

    media_root = current_app.config['MEDIA_ROOT']
    thumbnail_dir = current_app.config['THUMBNAIL_DIR']
    placeholder_url = current_app.config['PLACEHOLDER_URL']

    folder = request.args.get('folder')
    media_type = request.args.get('display')

    # Validate the folder path
    folder_path = validate_and_get_folder_path(media_root, folder)
    if not folder_path:
        return "Folder not found", 404

    # Get random files (never cached - always shuffles)
    try:
        media = get_sorted_files(media_root, folder_path, sort_by="random", include_dimensions=False, use_cache=False)
        print(f"Retrieved {len(media)} media files for random shuffle")
    except Exception as e:
        print(f"Error getting files: {e}")
        return f"Error retrieving files: {str(e)}", 500

    # Filter by media type if specified
    if media_type == 'images':
        media = [item for item in media if is_image(item['path'])]
    elif media_type == 'videos':
        media = [item for item in media if is_video(item['path'])]

    # Show first 100 random items (no pagination)
    max_items = 100
    random_media = media[:max_items]

    # Extract dimensions only for items we're showing
    add_dimensions_to_items(random_media, media_root, thumbnail_dir)

    # List all subfolders for dropdown
    folders = list_subfolders(media_root)

    # Count different media types for the UI
    image_count = len([item for item in media if is_image(item['path'])])
    video_count = len([item for item in media if is_video(item['path'])])
    total_count = len(media)

    # Render random template with shuffle button
    return render_template(
        'random.html',
        media_files=random_media,
        placeholder=placeholder_url,
        folders=folders,
        current_folder=folder,
        media_type=media_type,
        image_count=image_count,
        video_count=video_count,
        total_count=total_count,
        timestamp=int(time.time())  # For cache busting
    )


@bp.route('/new')
def new_gallery():
    """
    Gallery view sorted by newest items first with optional folder filtering.
    """
    folder = request.args.get('folder')  # Optional folder query parameter
    media_type = request.args.get('display')  # Get display filter parameter
    return handle_gallery(folder=folder, sort_by="new", media_type=media_type)


@bp.route('/api/stats')
def api_stats():
    """
    API endpoint that returns media collection statistics as JSON.
    Used by the home page to display stats in the hero section.
    """
    from flask import jsonify

    media_root = current_app.config['MEDIA_ROOT']

    try:
        # Get all media files (use cache for speed)
        media = get_sorted_files(media_root, media_root, sort_by="default", include_dimensions=False)

        # Count by type
        image_count = len([item for item in media if is_image(item['path'])])
        video_count = len([item for item in media if is_video(item['path'])])
        total_count = len(media)

        # Count folders
        folders = list_subfolders(media_root)
        folder_count = len(folders)

        return jsonify({
            'total_files': total_count,
            'image_count': image_count,
            'video_count': video_count,
            'folder_count': folder_count
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({
            'total_files': 0,
            'image_count': 0,
            'video_count': 0,
            'folder_count': 0,
            'error': str(e)
        }), 500
