# API Reference - Py Home Gallery

## Overview

Py Home Gallery provides both HTML views and JSON API endpoints for accessing media and metadata.

## Base URL

All API endpoints are relative to the server root:
- Development: `http://localhost:8000`
- Production: `http://your-server:port`

## HTML Views

### Home Page

**Endpoint**: `GET /`

**Description**: Home page with mosaic background and navigation options.

**Response**: HTML page

**Example**:
```bash
curl http://localhost:8000/
```

### Browse Page

**Endpoint**: `GET /browse`

**Description**: 3D Cover Flow browse page for folder navigation.

**Response**: HTML page

**Example**:
```bash
curl http://localhost:8000/browse
```

### Gallery View

**Endpoint**: `GET /gallery`

**Description**: Standard gallery view with pagination.

**Query Parameters**:
- `folder` (optional): Subfolder to filter by
- `display` (optional): Filter by media type (`images`, `videos`, or `all`)
- `page` (optional): Page number (default: 1)

**Response**: HTML page

**Examples**:
```bash
# Default gallery
curl http://localhost:8000/gallery

# Filter by folder
curl http://localhost:8000/gallery?folder=Photos

# Filter by media type
curl http://localhost:8000/gallery?display=videos

# Specific page
curl http://localhost:8000/gallery?page=2
```

### Random Gallery

**Endpoint**: `GET /random`

**Description**: Gallery view with randomized order.

**Query Parameters**: Same as `/gallery`

**Response**: HTML page

**Example**:
```bash
curl http://localhost:8000/random
```

### Newest Gallery

**Endpoint**: `GET /new`

**Description**: Gallery view sorted by newest files first.

**Query Parameters**: Same as `/gallery`

**Response**: HTML page

**Example**:
```bash
curl http://localhost:8000/new
```

### Infinite Scroll View

**Endpoint**: `GET /infinite`

**Description**: Infinite scroll gallery view.

**Response**: HTML page

**Example**:
```bash
curl http://localhost:8000/infinite
```

## JSON API Endpoints

### Browse API

**Endpoint**: `GET /api/browse`

**Description**: Returns all subfolders with random vertical thumbnails for Cover Flow display.

**Response**: JSON object

**Response Format**:
```json
[
  {
    "folder": "Photos",
    "thumbnail": "/thumbnail/Photos/image.jpg",
    "count": 150
  },
  {
    "folder": "Videos",
    "thumbnail": "/thumbnail/Videos/video.mp4.png",
    "count": 25
  }
]
```

**Example**:
```bash
curl http://localhost:8000/api/browse
```

**Response Fields**:
- `folder` (string): Folder name
- `thumbnail` (string): Path to random vertical thumbnail
- `count` (integer): Number of media files in folder

### Gallery Data

**Endpoint**: `GET /gallery-data`

**Description**: Returns paginated gallery data for infinite scroll.

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `folder` (optional): Subfolder to filter by
- `display` (optional): Filter by media type (`images`, `videos`, or `all`)

**Response**: JSON object

**Response Format**:
```json
{
  "items": [
    {
      "path": "photo1.jpg",
      "thumbnail": "/thumbnail/photo1.jpg",
      "width": 1920,
      "height": 1080
    }
  ],
  "page": 1,
  "total_pages": 10,
  "has_next": true
}
```

**Example**:
```bash
curl http://localhost:8000/gallery-data?page=1
```

**Response Fields**:
- `items` (array): Array of media file objects
- `page` (integer): Current page number
- `total_pages` (integer): Total number of pages
- `has_next` (boolean): Whether there is a next page

**Media File Object**:
- `path` (string): Relative path to media file
- `thumbnail` (string): Path to thumbnail
- `width` (integer): Media width in pixels
- `height` (integer): Media height in pixels

### Metadata API

**Endpoint**: `GET /api/metadata/<path:media_path>`

**Description**: Returns metadata for a specific media file.

**Path Parameters**:
- `media_path`: Relative path to the media file

**Response**: JSON object

**Response Format**:
```json
{
  "success": true,
  "path": "photo.jpg",
  "metadata": {
    "File": {
      "Name": "photo.jpg",
      "Size": "2.5 MB",
      "Modified": "2024-12-15 10:30:00"
    },
    "Image": {
      "Dimensions": "1920x1080",
      "Format": "JPEG"
    }
  },
  "raw": {
    "file_size": 2621440,
    "width": 1920,
    "height": 1080
  }
}
```

**Example**:
```bash
curl http://localhost:8000/api/metadata/photo.jpg
```

**Response Fields**:
- `success` (boolean): Whether request was successful
- `path` (string): Media file path
- `metadata` (object): Formatted metadata for display
- `raw` (object, optional): Raw metadata (if JSON serializable)

**Error Response**:
```json
{
  "success": false,
  "error": "File not found"
}
```

**Status Codes**:
- `200`: Success
- `403`: Invalid file path (path traversal attempt)
- `404`: File not found
- `500`: Internal server error

### Mosaic API

**Endpoint**: `GET /api/mosaic`

**Description**: Returns random thumbnails for mosaic background display.

**Query Parameters**:
- `count` (optional): Number of thumbnails to return (default: 100, max: 500)

**Response**: JSON object

**Response Format**:
```json
{
  "success": true,
  "thumbnails": [
    "/mosaic-thumb/photo1.jpg",
    "/mosaic-thumb/photo2.jpg"
  ],
  "count": 100,
  "requested": 100,
  "total": 500
}
```

**Example**:
```bash
# Get 50 random thumbnails
curl http://localhost:8000/api/mosaic?count=50

# Get 200 random thumbnails
curl http://localhost:8000/api/mosaic?count=200
```

**Response Fields**:
- `success` (boolean): Whether request was successful
- `thumbnails` (array): Array of thumbnail URLs
- `count` (integer): Number of thumbnails returned
- `requested` (integer): Number of thumbnails requested
- `total` (integer): Total number of thumbnails available

**Error Response**:
```json
{
  "success": false,
  "error": "Error message"
}
```

**Status Codes**:
- `200`: Success
- `500`: Internal server error

### Statistics API

**Endpoint**: `GET /api/stats`

**Description**: Returns gallery statistics for the home page hero section.

**Response**: JSON object

**Response Format**:
```json
{
  "total_files": 1250,
  "image_count": 1000,
  "video_count": 250,
  "folder_count": 4
}
```

**Example**:
```bash
curl http://localhost:8000/api/stats
```

**Response Fields**:
- `total_files` (integer): Total number of media files
- `image_count` (integer): Number of image files
- `video_count` (integer): Number of video files
- `folder_count` (integer): Number of subfolders in media directory

## Media Serving Endpoints

### Serve Media File

**Endpoint**: `GET /media/<path:filename>`

**Description**: Serves a media file (image or video).

**Path Parameters**:
- `filename`: Relative path to the media file

**Response**: Media file (image/video)

**Example**:
```bash
curl http://localhost:8000/media/photo.jpg
curl http://localhost:8000/media/videos/video.mp4
```

**Status Codes**:
- `200`: Success
- `400`: Invalid file type
- `403`: Access denied (path traversal attempt or permission denied)
- `404`: File not found
- `500`: Internal server error

### Serve Thumbnail

**Endpoint**: `GET /thumbnail/<path:filename>`

**Description**: Serves or generates a thumbnail for a media file.

**Path Parameters**:
- `filename`: Relative path to the media file

**Response**: Thumbnail image (PNG)

**Example**:
```bash
curl http://localhost:8000/thumbnail/photo.jpg
curl http://localhost:8000/thumbnail/videos/video.mp4
```

**Behavior**:
- If thumbnail exists: Serves thumbnail immediately
- If thumbnail doesn't exist: Queues generation and returns placeholder

**Status Codes**:
- `200`: Success
- `400`: Invalid file type
- `403`: Access denied
- `404`: File not found
- `500`: Internal server error

### Serve Mosaic Thumbnail

**Endpoint**: `GET /mosaic-thumb/<path:filename>`

**Description**: Serves a thumbnail for mosaic display (direct serving, no generation).

**Path Parameters**:
- `filename`: Relative path to the thumbnail file

**Response**: Thumbnail image

**Example**:
```bash
curl http://localhost:8000/mosaic-thumb/photo.jpg
```

**Status Codes**:
- `200`: Success
- `404`: Thumbnail not found

## Error Responses

All API endpoints return consistent error responses:

### 400 Bad Request

```json
{
  "error": "Invalid file type"
}
```

### 403 Forbidden

```json
{
  "error": "Access denied"
}
```

### 404 Not Found

```json
{
  "error": "File not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

## Security

All endpoints implement security checks:

1. **Extension Validation**: Only allowed media extensions are permitted
2. **Path Traversal Protection**: Paths are validated to prevent directory traversal
3. **File Existence**: Files are verified to exist before serving
4. **Permission Checks**: Read permissions are verified

See [Security Guide](SECURITY.md) for detailed information.

## Rate Limiting

Currently, there is no rate limiting implemented. For production deployments with external access, consider implementing rate limiting.

## CORS

CORS headers are included in media file responses for cross-origin access. API endpoints do not include CORS headers by default.

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Security Guide](SECURITY.md) - Security features
- [Features Guide](FEATURES.md) - Feature documentation

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

