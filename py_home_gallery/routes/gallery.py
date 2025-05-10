"""
Gallery route handlers for Py Home Gallery.

This module contains route handlers for the main gallery views,
including default, random, and newest-first sorting.
"""

from flask import Blueprint, render_template, request, current_app
from py_home_gallery.media.scanner import list_subfolders, validate_and_get_folder_path, get_sorted_files
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
    
    # Get sorted files from the specified folder
    try:
        media = get_sorted_files(media_root, folder_path, sort_by=sort_by)
        print(f"Retrieved {len(media)} media files from {folder_path}")
    except Exception as e:
        print(f"Error getting files: {e}")
        return f"Error retrieving files: {str(e)}", 500
    
    # Filter by media type if specified
    if media_type == 'images':
        media = [(path, thumb) for path, thumb in media if is_image(path)]
    elif media_type == 'videos':
        media = [(path, thumb) for path, thumb in media if is_video(path)]

    # Paginate the files
    page = int(request.args.get('page', 1))
    paginated_media, total_pages = paginate_items(media, page, items_per_page)

    # List all subfolders for dropdown
    folders = list_subfolders(media_root)

    # Count different media types for the UI
    image_count = len([(path, thumb) for path, thumb in media if is_image(path)])
    video_count = len([(path, thumb) for path, thumb in media if is_video(path)])
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
    Randomized gallery view with optional folder filtering.
    """
    folder = request.args.get('folder')  # Optional folder query parameter
    media_type = request.args.get('display')  # Get display filter parameter
    return handle_gallery(folder=folder, sort_by="random", media_type=media_type)


@bp.route('/new')
def new_gallery():
    """
    Gallery view sorted by newest items first with optional folder filtering.
    """
    folder = request.args.get('folder')  # Optional folder query parameter
    media_type = request.args.get('display')  # Get display filter parameter
    return handle_gallery(folder=folder, sort_by="new", media_type=media_type)
