# Py Home Gallery

A lightweight, Flask-based media gallery server designed for browsing and viewing your local media collection across your home network. Perfect for viewing photos and videos from any device, including smart TVs.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## Features

- **Multiple Gallery Views**: Default, random order, and newest-first sorting options
- **Automatic Video Thumbnails**: Generates thumbnails for videos using the middle frame
- **Responsive Grid Layout**: Using Isotope.js for masonry-style layout
- **Media Filtering**: Filter by media type (video/images) and folders
- **Pagination**: Standard page-based navigation for better performance
- **Infinite Scrolling**: Alternative view with dynamic content loading
- **Lightbox Viewer**: Full-screen viewing for both images and videos
- **Network Accessible**: Access your media from any device on your home network

## Demo

![Demo](./screenshots/demo.gif)
## Screenshots

![Screenshot 1](./screenshots/screenshot1.png)
![Screenshot 2](./screenshots/screenshot2.png)
![Screenshot 3](./screenshots/screenshot3.png)

## Installation

### Prerequisites

- Python 3.6+
- FFmpeg installed and accessible in PATH (required for video thumbnail generation)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/guinetik/py-home-gallery.git
   cd py-home-gallery
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application with your media directory:
   ```bash
   # Basic usage with just the media directory
   python run.py --media-dir "/path/to/your/media"
   
   # Specify a custom thumbnail directory
   python run.py --media-dir "/path/to/your/media" --thumbnail-dir "/custom/path/for/thumbnails"
   
   # Example with all options
   python run.py --media-dir "/home/guinetik/Media" --thumbnail-dir "/home/guinetik/gallery-thumbs" --port 8080 --items-per-page 100
   ```

4. The application will automatically create a thumbnail directory in your home folder:
   - Windows: `C:\Users\YourUsername\.py-home-gallery\thumbnails`
   - Linux/macOS: `~/.py-home-gallery/thumbnails`

5. The application will check if FFmpeg is installed and available in your PATH before starting.

6. Access the gallery:
   Open `http://localhost:8000` in your browser, or use your server's IP address to access it from other devices on your network.

## Usage

- **Main Dashboard**: Navigate to the home page to choose your gallery view
- **Default Gallery**: Standard gallery view with pagination
- **Random Gallery**: Same content but in randomized order
- **Newest First**: Gallery sorted by most recent files
- **Infinite Scrolling**: Continuously loads more content as you scroll
- **Folder Dropdown**: Filter media by folder
- **Media Type Filters**: View only images or only videos

## How It Works

Py Home Gallery scans your media directory for images and videos. For videos, it automatically generates thumbnails using FFmpeg/moviepy, which are stored in the thumbnail directory. The application serves both the thumbnails and the original media files through a Flask web server.

The gallery uses modern web technologies like Isotope.js for layout, GLightbox for the media viewer, and supports both traditional pagination and infinite scrolling for different viewing preferences.

## Configuration Options

Py Home Gallery supports the following command-line arguments:

```
--media-dir PATH       Root directory containing media files
                       (default: ./media)
                       ENV: PY_HOME_GALLERY_MEDIA_DIR

--thumbnail-dir PATH   Directory to store generated thumbnails
                       (default: ~/.py-home-gallery/thumbnails on Linux/Mac
                       or C:\Users\YourUsername\.py-home-gallery\thumbnails on Windows)
                       ENV: PY_HOME_GALLERY_THUMB_DIR

--items-per-page NUM   Number of items to display per page
                       (default: 50)
                       ENV: PY_HOME_GALLERY_ITEMS_PER_PAGE

--host HOST            Host to run the server on
                       (default: 0.0.0.0)
                       ENV: PY_HOME_GALLERY_HOST

--port PORT            Port to run the server on
                       (default: 8000)
                       ENV: PY_HOME_GALLERY_PORT

--placeholder URL      URL for placeholder thumbnails
                       (default: https://via.placeholder.com/300x200)
                       ENV: PY_HOME_GALLERY_PLACEHOLDER

--skip-ffmpeg-check    Skip the check for FFmpeg installation (use at your own risk)
```

The environment variables can be set differently depending on your shell:

### Command Prompt (CMD)
```cmd
SET PY_HOME_GALLERY_MEDIA_DIR=C:\path\to\media
SET PY_HOME_GALLERY_PORT=8080
```

### PowerShell
```powershell
$env:PY_HOME_GALLERY_MEDIA_DIR = "C:\path\to\media"
$env:PY_HOME_GALLERY_PORT = "8080"
```

### Bash/Linux/macOS
```bash
export PY_HOME_GALLERY_MEDIA_DIR="/path/to/media"
export PY_HOME_GALLERY_PORT="8080"
```

## Common Usage Examples

### Basic Usage (Windows - CMD)
Start the server with the default settings but point to your media directory:
```cmd
python run.py --media-dir "%USERPROFILE%\Media"
```

### Basic Usage (Windows - PowerShell)
Start the server with the default settings but point to your media directory:
```powershell
python run.py --media-dir "$env:USERPROFILE\Media"
```

### Change Server Port (Windows - CMD)
Run on a different port (useful if port 8000 is already in use):
```cmd
python run.py --media-dir "%USERPROFILE%\Media" --port 8080
```

### Change Server Port (Windows - PowerShell)
Run on a different port (useful if port 8000 is already in use):
```powershell
python run.py --media-dir "$env:USERPROFILE\Media" --port 8080
```

### Specify Thumbnail Location (Windows - CMD)
Store thumbnails in a custom location:
```cmd
python run.py --media-dir "%USERPROFILE%\Media" --thumbnail-dir "D:\thumbnails"
```

### Specify Thumbnail Location (Windows - PowerShell)
Store thumbnails in a custom location:
```powershell
python run.py --media-dir "$env:USERPROFILE\Media" --thumbnail-dir "D:/thumbnails"
```

### Using Environment Variables (Windows - CMD)
You can also set options using environment variables in Command Prompt:
```cmd
:: Set options via environment variables
SET PY_HOME_GALLERY_MEDIA_DIR=%USERPROFILE%\Media
SET PY_HOME_GALLERY_PORT=8080

:: Then run without command-line arguments
python run.py
```

### Using Environment Variables (Windows - PowerShell)
You can also set options using environment variables in PowerShell:
```powershell
# Set options via environment variables
$env:PY_HOME_GALLERY_MEDIA_DIR = "$env:USERPROFILE\Media"
$env:PY_HOME_GALLERY_PORT = "8080"

# Then run without command-line arguments
python run.py
```

### Multiple-Instance Setup (Windows - CMD)
Run multiple instances for different media collections:
```cmd
:: Run first instance for photos
python run.py --media-dir "%USERPROFILE%\Pictures" --port 8000

:: Run second instance for videos on a different port
python run.py --media-dir "%USERPROFILE%\Videos" --port 8001
```

### Multiple-Instance Setup (Windows - PowerShell)
Run multiple instances for different media collections:
```powershell
# Run first instance for photos
python run.py --media-dir "$env:USERPROFILE\Pictures" --port 8000

# Run second instance for videos on a different port
python run.py --media-dir "$env:USERPROFILE\Videos" --port 8001
```

### Basic Usage (Linux/macOS)
Start the server with the default settings but point to your media directory:
```bash
python run.py --media-dir "/home/guinetik/Media"
# OR using home directory shorthand
python run.py --media-dir "~/Media"
```

### Change Server Port (Linux/macOS)
Run on a different port (useful if port 8000 is already in use):
```bash
python run.py --media-dir "~/Media" --port 8080
```

### Specify Thumbnail Location (Linux/macOS)
Store thumbnails in a custom location:
```bash
python run.py --media-dir "~/Media" --thumbnail-dir "/mnt/external/thumbnails"
```

### Using Environment Variables (Linux/macOS)
You can also set options using environment variables:
```bash
# Set options via environment variables
export PY_HOME_GALLERY_MEDIA_DIR="$HOME/Media"
export PY_HOME_GALLERY_PORT="8080"

# Then run without command-line arguments
python run.py
```

### Multiple-Instance Setup (Linux/macOS)
Run multiple instances for different media collections:
```bash
# Run first instance for photos
python run.py --media-dir "~/Photos" --port 8000

# Run second instance for videos on a different port
python run.py --media-dir "~/Videos" --port 8001
```

### Notes on Windows Path Syntax

On Windows, path handling differs between Command Prompt (CMD) and PowerShell:

#### Command Prompt (CMD)

1. Use environment variables with percent signs: `python run.py --media-dir "%USERPROFILE%\Media"`
2. Escape backslashes by doubling them: `python run.py --media-dir "C:\Users\guinetik\Media"`
3. Or use forward slashes: `python run.py --media-dir "C:/Users/guinetik/Media"`

#### PowerShell

1. Use environment variables with `$env:`: `python run.py --media-dir "$env:USERPROFILE\Media"`
2. Use forward slashes to avoid escape issues: `python run.py --media-dir "C:/Users/guinetik/Media"`
3. Or use the `-f` string formatting to handle backslashes properly: 
   ```powershell
   $mediaDir = "{0}\Media" -f $env:USERPROFILE
   python run.py --media-dir "$mediaDir"
   ```

The tilde (`~`) shorthand for home directory doesn't work in Windows terminals. Use `%USERPROFILE%` (CMD) or `$env:USERPROFILE` (PowerShell) instead.

## Customization

- **Thumbnail Size**: Modify the thumbnail dimensions in the `serve_thumbnail` function
- **Styling**: Customize the appearance by modifying the CSS in the HTML templates

## Recommended Use

This application works great as a simple home media server. Set it up on a computer that's always on (or a Raspberry Pi), transfer media from your phone using your preferred sync method, and access it from any device in your home, including smart TVs, via a web browser.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Isotope.js](https://isotope.metafizzy.co/)
- [GLightbox](https://biati-digital.github.io/glightbox/)
- [MoviePy](https://zulko.github.io/moviepy/)