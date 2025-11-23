# Features - Py Home Gallery

## Overview

Py Home Gallery provides a comprehensive set of features for browsing and viewing your local media collection. This document describes all available features and how to use them.

## Core Features

### Multiple Gallery Views

Py Home Gallery offers several ways to browse your media:

#### Default Gallery (`/gallery`)
Standard gallery view with pagination. Displays media in a masonry grid layout with pagination controls.

**Features**:
- Pagination for better performance
- Folder filtering
- Media type filtering (images/videos)
- Responsive grid layout

**Usage**:
- Navigate to `/gallery` or click "Gallery" from home page
- Use pagination controls to navigate pages
- Use folder dropdown to filter by folder
- Use media type buttons to filter by type

#### Random Gallery (`/random`)
Same as default gallery but with randomized order. Great for discovering forgotten photos.

**Usage**:
- Navigate to `/random` or click "Shuffle" from home page
- Media appears in random order each time

#### Newest First (`/new`)
Gallery sorted by most recent files first. Shows your latest photos and videos at the top.

**Usage**:
- Navigate to `/new` or click "Newest" from home page
- Most recently modified files appear first

#### Infinite Scroll (`/infinite`)
Continuously loads more content as you scroll. No pagination needed.

**Features**:
- Automatic loading as you scroll
- Smooth scrolling experience
- Same filtering options as other views

**Usage**:
- Navigate to `/infinite` or click "Infinite Scroll" from home page
- Scroll down to load more content automatically

### Browse Page - 3D Cover Flow

**Endpoint**: `/browse`

An iPod-inspired 3D carousel interface for browsing folders. Provides an intuitive way to navigate your media collection by folder.

**Features**:
- 3D card rotation (40°-60° angles)
- Up to 7 visible cards (center + 3 on each side)
- Smooth animations and transitions
- Multiple navigation methods

**Navigation Methods**:
- **Keyboard**: Arrow keys to navigate, Enter to select
- **Mouse Wheel**: Scroll to navigate (with throttling)
- **Touch Swipe**: Swipe gestures on touch devices
- **Mouse Drag**: Click and drag to navigate
- **Click**: Click any card to center it

**Visual Features**:
- Parallax mouse movement effect (carousel tilts based on cursor position)
- Intro animations (staggered card entrance)
- Glassmorphism cards with folder name and item count
- Hover effects (active card scales with blue border)
- Vertical thumbnail prioritization for folder covers

**Responsive Card Sizes**:
- Mobile (≤768px): 312px × 480px
- Desktop (default): 420px × 600px
- Full HD (≥1600px): 540px × 780px
- 4K (≥2400px): 660px × 960px

All cards feature square corners (0px border-radius) matching the site-wide aesthetic.

**Usage**:
- Navigate to `/browse` or click "Browse" from home page
- Use any navigation method to browse folders
- Click a folder card to view its contents

### Home Page with Living Mosaic

**Endpoint**: `/`

The home page features a dynamic mosaic background that continuously updates for a living screensaver effect.

**Features**:
- **Grid-aligned mosaic**: Fixed 150px square cells that fill the viewport
- **Auto-shuffling**: Every 10 seconds, randomly picks 1-5 tiles and replaces them with new random photos
- **Intelligent tiling**: Automatically repeats thumbnails if collection is smaller than grid size
- **Staggered loading**: Photos fade in with random delays (0-2 seconds) for organic appearance
- **Responsive sizing**: Grid adapts to all screen resolutions
- **Navigation cards**: Grid-aligned glassmorphic cards for Browse, Gallery, Shuffle, Newest, and Infinite Scroll
- **Theme toggle**: Dark/light mode with localStorage persistence

**How It Works**:
1. On page load, creates a grid based on viewport size (width ÷ 150px × height ÷ 150px)
2. Fetches random thumbnails from `/api/mosaic?count=<cells>`
3. If fewer thumbnails than cells, repeats thumbnails to fill entire grid
4. Every 10 seconds, picks 1-5 random cells, fades them out, fetches new thumbnails, fades them in
5. Creates continuous living photo display

**Usage**:
- Navigate to `/` to see the home page
- Watch as tiles automatically update every 10 seconds
- Click any navigation card to go to that view
- Toggle theme using the theme button (top right)

### Automatic Video Thumbnails

Videos automatically get thumbnails generated using the middle frame of the video.

**Features**:
- Automatic generation on first access
- Background generation (non-blocking)
- Fallback to placeholder if generation fails
- Cached thumbnails for performance

**How it works**:
1. First request for video thumbnail queues generation
2. Placeholder is returned immediately
3. Background worker generates thumbnail
4. Next request gets the real thumbnail

**Supported Formats**:
- MP4, MOV, AVI, MKV, WebM, FLV

### Media Filtering

Filter media by type and folder for easier browsing.

#### Media Type Filtering

Filter to show only images or only videos:

- **All**: Shows both images and videos (default)
- **Images**: Shows only image files
- **Videos**: Shows only video files

**Usage**:
- Click filter buttons in gallery view
- Filter persists across pagination
- Works with all gallery views

#### Folder Filtering

Filter media by folder using the folder dropdown:

- Shows all subfolders in media directory
- Select folder to filter media
- Works with all gallery views

**Usage**:
- Use folder dropdown in gallery view
- Select folder to filter
- Select "All Folders" to show everything

### Pagination

Standard page-based navigation for better performance with large collections.

**Features**:
- Configurable items per page (default: 50)
- Page navigation controls
- Total page count display
- Works with all filtering options

**Configuration**:
```bash
python run.py --items-per-page 100
```

### Lightbox Viewer

Full-screen viewing for both images and videos.

**Features**:
- Click any media item to open in lightbox
- Keyboard navigation (arrow keys)
- Close with Escape key or close button
- Video playback support
- Smooth transitions

**Usage**:
- Click any media item in gallery
- Use arrow keys to navigate
- Press Escape to close

### Theme System

Dark and light theme toggle with localStorage persistence.

**Features**:
- Dark mode and light mode
- Theme preference saved in browser
- Site-wide theme application
- Smooth theme transitions

**Usage**:
- Click theme toggle button (top right)
- Theme preference is saved automatically
- Theme persists across sessions

### Responsive Design

Works seamlessly on desktop, tablet, and mobile devices with a modern square aesthetic.

**Design System**:
- **Square Aesthetic**: Sharp corners throughout (0px border-radius) for modern, grid-aligned look
- **Grid Alignment**: All elements snap to 150px grid cells on homepage
- **Responsive Sizing**: Content width adapts proportionally to viewport
  - Mobile: 2-4 grid columns
  - Tablet: 4-6 grid columns
  - Desktop: 8 grid columns (1200px)
  - Elements resize based on available grid columns

**Features**:
- Responsive grid layout
- Touch-friendly controls
- Mobile-optimized navigation
- Adaptive card sizes
- Square-cornered thumbnails and cards
- Grid-aligned homepage elements

**Breakpoints**:
- Mobile (≤768px): Single column cards, compact stats, optimized touch targets
- Tablet (768-1600px): Two column cards, medium sizing
- Desktop (1600-2400px): Four column cards, standard sizing
- Full HD (1600-2400px): Larger carousel cards (540px)
- 4K (≥2400px): Extra large carousel cards (660px)

## Performance Features

### Caching System

Directory scans are cached to improve performance.

**Features**:
- 5-minute cache TTL (configurable)
- Automatic cache expiration
- Manual cache invalidation
- Significant performance improvement

**Configuration**:
```bash
python run.py --cache-ttl 600
```

See [Cache and Workers Guide](CACHE_AND_WORKERS.md) for details.

### Background Workers

Thumbnail generation happens in background threads.

**Features**:
- Non-blocking thumbnail generation
- Configurable thread count
- Queue-based processing
- Immediate response with placeholder

**Configuration**:
```bash
python run.py --worker-threads 4
```

See [Cache and Workers Guide](CACHE_AND_WORKERS.md) for details.

## Security Features

### Path Traversal Protection

Complete protection against directory traversal attacks.

**Features**:
- All paths validated before access
- Multiple security layers
- Security events logged

See [Security Guide](SECURITY.md) for details.

### Input Validation

All user inputs are validated and sanitized.

**Features**:
- Extension validation
- Path validation
- Filename sanitization

See [Security Guide](SECURITY.md) for details.

## Network Access

Access your media from any device on your home network.

**Features**:
- Access from any device (desktop, tablet, phone, smart TV)
- Works on local network
- No external dependencies

**Usage**:
1. Start server: `python run.py --host 0.0.0.0`
2. Find your server IP address
3. Access from any device: `http://your-ip:8000`

## Metadata Display

View detailed metadata for media files.

**Features**:
- File information (size, date, format)
- Image metadata (dimensions, EXIF data)
- Video metadata (duration, codec, resolution)
- Click media item to view metadata

**Usage**:
- Click any media item
- View metadata in lightbox or detail view
- Metadata API available at `/api/metadata/<path>`

## Supported Media Formats

### Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

### Videos
- MP4 (.mp4)
- MOV (.mov)
- AVI (.avi)
- MKV (.mkv)
- WebM (.webm)
- FLV (.flv)

## Feature Comparison

| Feature | Default Gallery | Random | Newest | Infinite | Browse |
|---------|----------------|--------|--------|----------|--------|
| Pagination | ✅ | ✅ | ✅ | ❌ | ❌ |
| Folder Filter | ✅ | ✅ | ✅ | ✅ | N/A |
| Type Filter | ✅ | ✅ | ✅ | ✅ | N/A |
| Sorting | Default | Random | Newest | Default | N/A |
| Infinite Load | ❌ | ❌ | ❌ | ✅ | ❌ |
| 3D Navigation | ❌ | ❌ | ❌ | ❌ | ✅ |

## Usage Examples

### View All Photos

1. Navigate to `/gallery`
2. Click "Images" filter button
3. Browse through pages

### Find Latest Videos

1. Navigate to `/new`
2. Click "Videos" filter button
3. Latest videos appear at top

### Browse by Folder

1. Navigate to `/browse`
2. Use arrow keys or mouse wheel to navigate folders
3. Press Enter or click folder to view contents

### View Specific Folder

1. Navigate to `/gallery`
2. Select folder from dropdown
3. Browse folder contents

### Infinite Scroll Experience

1. Navigate to `/infinite`
2. Scroll down to automatically load more
3. No pagination needed

## Related Documentation

- [API Reference](API.md) - API endpoints
- [Configuration Guide](CONFIGURATION.md) - Configuration options
- [Architecture Guide](ARCHITECTURE.md) - System architecture

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

