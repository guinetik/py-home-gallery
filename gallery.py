"""
Media Gallery with Flask and Video Thumbnails (Optimized Startup)

This script parses a media directory and generates video thumbnails at startup.
The media list is cached globally, and thumbnails are only generated for videos
that do not already have one. If a thumbnail is missing, a placeholder is used.

Dependencies:
    - Flask >= 2.0.0
    - Pillow >= 7.0.0
    - moviepy == 1.0.3
    - numpy >= 1.18.1
    - imageio >= 2.5.0
    - decorator >= 4.3.0
    - tqdm >= 4.0.0
    - scipy >= 1.3.0
    - pydub >= 0.23.0
    - audiofile >= 0.0.0
    - opencv-python >= 4.5
    - ffmpeg installed and accessible in PATH (used by moviepy)

Features:
    - Directory traversal and thumbnail generation happen at startup.
    - Placeholders for missing video thumbnails to ensure responsiveness.
    - Pagination for better performance with large directories.

"""
import random
import argparse
import sys
import subprocess
from flask import Flask, render_template, send_file, request, jsonify
from moviepy import VideoFileClip
from PIL import Image
import os

# Function to check if FFmpeg is installed
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

# Parse command-line arguments
def parse_arguments():
    """
    Parse command-line arguments for the application.
    """
    parser = argparse.ArgumentParser(description='Media Gallery Server')
    
    parser.add_argument(
        '--media-dir', 
        type=str, 
        default=os.environ.get('PY_HOME_GALLERY_MEDIA_DIR', './media'),
        help='Root directory containing media files (default: ./media). '
             'ENV: PY_HOME_GALLERY_MEDIA_DIR (CMD: %%USERPROFILE%%\\Media, PowerShell: $env:USERPROFILE\\Media)'
    )
    
    # Default thumbnail directory in user's home directory (cross-platform)
    default_thumb_dir = os.path.join(os.path.expanduser('~'), '.py-home-gallery', 'thumbnails')
    
    parser.add_argument(
        '--thumbnail-dir', 
        type=str, 
        default=os.environ.get('PY_HOME_GALLERY_THUMB_DIR', default_thumb_dir),
        help='Directory to store generated thumbnails '
             '(default: ~/.py-home-gallery/thumbnails on Linux/Mac or C:\\Users\\YourUsername\\.py-home-gallery\\thumbnails on Windows). '
             'ENV: PY_HOME_GALLERY_THUMB_DIR'
    )
    
    parser.add_argument(
        '--items-per-page', 
        type=int, 
        default=int(os.environ.get('PY_HOME_GALLERY_ITEMS_PER_PAGE', '50')),
        help='Number of items to display per page (default: 50). '
             'ENV: PY_HOME_GALLERY_ITEMS_PER_PAGE'
    )
    
    parser.add_argument(
        '--host', 
        type=str, 
        default=os.environ.get('PY_HOME_GALLERY_HOST', '0.0.0.0'),
        help='Host to run the server on (default: 0.0.0.0). '
             'ENV: PY_HOME_GALLERY_HOST'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=int(os.environ.get('PY_HOME_GALLERY_PORT', '8000')),
        help='Port to run the server on (default: 8000). '
             'ENV: PY_HOME_GALLERY_PORT'
    )
    
    parser.add_argument(
        '--placeholder', 
        type=str, 
        default=os.environ.get('PY_HOME_GALLERY_PLACEHOLDER', 'https://via.placeholder.com/300x200'),
        help='URL for placeholder thumbnails (default: https://via.placeholder.com/300x200). '
             'ENV: PY_HOME_GALLERY_PLACEHOLDER'
    )
    
    parser.add_argument(
        '--skip-ffmpeg-check',
        action='store_true',
        help='Skip the check for FFmpeg installation (use at your own risk)'
    )
    
    return parser.parse_args()

# Initialize Flask app
app = Flask(__name__)

# Global variable to store media metadata
media_files = []

# Global configuration variables (will be set from command-line args)
MEDIA_ROOT = None
THUMBNAIL_DIR = None
ITEMS_PER_PAGE = None
PLACEHOLDER_URL = None

def list_subfolders(directory):
    """
    List all subfolders in a given directory.
    """
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

def validate_and_get_folder_path(folder):
    """
    Validate the folder and return its absolute path.
    If no folder is specified, return the root media directory.
    """
    folder_path = os.path.join(MEDIA_ROOT, folder) if folder else MEDIA_ROOT
    if folder and (not os.path.exists(folder_path) or not os.path.isdir(folder_path)):
        return None  # Invalid folder
    return folder_path


def paginate_items(items, page, items_per_page):
    """
    Paginate a list of items.
    """
    start = (page - 1) * items_per_page
    end = start + items_per_page
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    return items[start:end], total_pages


def get_sorted_files(folder_path, sort_by="default"):
    """
    Get files from a folder and optionally sort them.
    Sorting options:
    - "random": Randomize order
    - "new": Sort by newest files first
    - "default": No specific order
    """
    media = scan_directory(folder_path)

    if sort_by == "random":
        random.shuffle(media)
    elif sort_by == "new":
        media = sorted(media, key=lambda x: os.path.getmtime(os.path.join(MEDIA_ROOT, x[0])), reverse=True)

    return media


def scan_directory(directory):
    """
    Recursively scans a directory for media files (images and videos).
    """
    media = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.mkv')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=MEDIA_ROOT)

                # For videos, use a separate thumbnail generation logic
                if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    thumb_path = os.path.join(THUMBNAIL_DIR, f"{os.path.basename(file)}.png")
                    media.append((rel_path, f"/thumbnail/{rel_path}"))
                else:
                    # For images, prepend `/media/` to the path for direct serving
                    media.append((rel_path, f"/media/{rel_path}"))  # Image uses itself as the thumbnail
    return media
    
def handle_gallery(folder=None, sort_by="default"):
    """
    Unified handler for gallery endpoints.
    - folder: Subfolder to filter files.
    - sort_by: Sorting method ('default', 'random', 'new').
    """
    folder_path = validate_and_get_folder_path(folder)
    if not folder_path:
        return "Folder not found", 404

    # Get sorted files
    media = get_sorted_files(folder_path, sort_by=sort_by)

    # Paginate the files
    page = int(request.args.get('page', 1))
    paginated_media, total_pages = paginate_items(media, page, ITEMS_PER_PAGE)

    # List all subfolders for dropdown
    folders = list_subfolders(MEDIA_ROOT)

    # Render the template
    return render_template(
        'gallery.html',
        media_files=paginated_media,
        page=page,
        total_pages=total_pages,
        placeholder=PLACEHOLDER_URL,
        folders=folders,
        current_folder=folder,
    )


@app.route('/')
def index():
    """
    Index page with buttons to navigate to different gallery views.
    """
    return render_template('index.html')


@app.route('/gallery')
def gallery():
    """
    Default gallery view with optional folder filtering and pagination.
    """
    folder = request.args.get('folder')  # Get folder query parameter
    return handle_gallery(folder=folder, sort_by="default")


@app.route('/random')
def random_gallery():
    """
    Randomized gallery view with optional folder filtering.
    """
    folder = request.args.get('folder')  # Optional folder query parameter
    return handle_gallery(folder=folder, sort_by="random")


@app.route('/new')
def new_gallery():
    """
    Gallery view sorted by newest items first with optional folder filtering.
    """
    folder = request.args.get('folder')  # Optional folder query parameter
    return handle_gallery(folder=folder, sort_by="new")


@app.route('/thumbnail/<path:filename>')
def serve_thumbnail(filename):
    """
    Serve generated thumbnails for videos, creating them on-demand if missing.
    """
    video_path = os.path.join(MEDIA_ROOT, filename)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{os.path.basename(filename)}.png")

    # Generate thumbnail if it doesn't exist
    if not os.path.exists(thumbnail_path):
        try:
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(clip.duration / 2)  # Take a frame from the middle
            clip.close()

            # Save the frame as a thumbnail
            image = Image.fromarray(frame)
            image.thumbnail((300, 200))
            image.save(thumbnail_path)
        except Exception as e:
            print(f"Error generating thumbnail for {video_path}: {e}")
            return PLACEHOLDER_URL

    return send_file(thumbnail_path)
    
@app.route('/media/<path:filename>')
def serve_media(filename):
    """
    Serve media files.
    """
    return send_file(os.path.join(MEDIA_ROOT, filename))


@app.route('/infinite')
def infinite_gallery():
    """
    Serve the infinite scrolling gallery page with the initial set of media.
    """
    global media_files

    if not media_files:
        media_files = scan_directory(MEDIA_ROOT)

    # Sort by newest first
    sorted_files = sorted(media_files, key=lambda x: os.path.getmtime(os.path.join(MEDIA_ROOT, x[0])), reverse=True)

    # Load the first page
    start = 0
    end = ITEMS_PER_PAGE
    initial_files = sorted_files[start:end]

    return render_template(
        'infinite.html',
        media_files=initial_files,
        placeholder=PLACEHOLDER_URL
    )


@app.route('/gallery-data')
def gallery_data():
    """
    Serve paginated media data for infinite scrolling.
    """
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort', 'default')  # Default sorting

    global media_files
    if not media_files:
        media_files = scan_directory(MEDIA_ROOT)

    if sort_by == 'new':
        # Sort by last modification time
        media_files = sorted(media_files, key=lambda x: os.path.getmtime(os.path.join(MEDIA_ROOT, x[0])), reverse=True)

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    media_slice = media_files[start:end]
    total_pages = (len(media_files) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    return jsonify({
        'media': [{'path': media, 'thumbnail': thumbnail} for media, thumbnail in media_slice],
        'has_next': page < total_pages
    })

def main():
    """
    Main entry point for the application.
    Parses arguments, validates environment, and starts the server.
    """
    global MEDIA_ROOT, THUMBNAIL_DIR, ITEMS_PER_PAGE, PLACEHOLDER_URL
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Check for FFmpeg installation if not skipped
    if not args.skip_ffmpeg_check and not check_ffmpeg():
        print("Error: FFmpeg not found in PATH. FFmpeg is required for video thumbnail generation.")
        print("Please install FFmpeg and make sure it's accessible in your PATH, or use --skip-ffmpeg-check to bypass this check.")
        sys.exit(1)
    
    # Set global configuration from arguments
    MEDIA_ROOT = os.path.abspath(args.media_dir)
    THUMBNAIL_DIR = os.path.abspath(args.thumbnail_dir)
    ITEMS_PER_PAGE = args.items_per_page
    PLACEHOLDER_URL = args.placeholder
    
    # Validate media directory
    if not os.path.exists(MEDIA_ROOT):
        print(f"Error: Media directory '{MEDIA_ROOT}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(MEDIA_ROOT):
        print(f"Error: Media path '{MEDIA_ROOT}' is not a directory.")
        sys.exit(1)
    
    # Create thumbnail directory if it doesn't exist
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
    
    # Display configuration
    print(f"Media Gallery Server Configuration:")
    print(f"Media Directory: {MEDIA_ROOT}")
    print(f"Thumbnail Directory: {THUMBNAIL_DIR}")
    print(f"Items Per Page: {ITEMS_PER_PAGE}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    
    # Start the server
    app.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()