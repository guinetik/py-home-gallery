# CHANGELOG

## 0.2.0 - 2025-11-23

### 🏭 Added

- **Browse page with 3D Cover Flow carousel** - iPod-inspired interface for folder navigation
- `/api/browse` endpoint - returns all folders with random vertical thumbnail previews
- **Multiple navigation methods:**
  - Keyboard (arrow keys, Enter)
  - Mouse wheel with throttling
  - Touch swipe gestures
  - Mouse drag
  - Click on any card to center it
- **Parallax mouse movement effect** - carousel tilts subtly based on cursor position (max 5° on X/Y axes)
- **Intro animations** - staggered card entrance with fade-in and scale-up effect
- **Responsive scaling** - optimized layouts for mobile (260px cards), desktop (350px), Full HD (450px), and 4K (550px)

### ⚡ Performance

- GPU-optimized rendering without heavy reflection effects
- Animation locking prevents navigation during transitions (eliminates visible card jumping)
- Mouse wheel throttling (400ms cooldown) for smooth scrolling
- Smooth wrap-around with opacity fade - cards invisible during position changes
- Cross-browser compatible flexbox layout (Firefox, Chrome, Safari)

### 🎨 Design

- Classic Cover Flow aesthetic with 3D card rotation (40°-60° angles)
- Up to 7 visible cards (center + 3 on each side) with depth positioning
- Vertical thumbnail prioritization for folder covers (portrait images preferred)
- Glassmorphism cards with folder name and item count
- Hover effects - active card scales to 1.05x with blue border accent
- Text positioned above image (cleaner look, no text in reflection area)
- Cards scale proportionally across screen sizes with proper 3D perspective depth

### 💡 Fixed

- Image alignment with card rounded corners (14px bottom radius)
- Cross-browser image sizing consistency using flexbox
- Text selection disabled during swipe gestures
- Gap between card and image eliminated with flex layout

## 0.1.0 - 2025-11-23

### 🏭 Added

- Docker deployment with Nginx for production use
- Environment-based configuration via `.env` file
- Site-wide dark/light mode theme system with localStorage persistence
- New home page with modern card-based design and live stats
- API endpoint `/api/stats` for media collection statistics
- Random gallery page with shuffle button (replaces pagination)
- Theme toggle button in navigation bar
- Production mode flag and serve-media configuration

### ⚡ Performance

- Implemented mtime caching during directory scan (eliminates repeated filesystem calls)
- Added sorted results caching with unique keys per sort type
- Progressive Isotope layout - re-layout on each image load to prevent overlaps
- Nginx serves static files (3-5x faster than Flask)

### 💡 Fixed

- Cache corruption bug from in-place list modification in random shuffle
- Duplicate logging from child logger propagation
- Infinite scroll broken due to missing grid element return
- Navbar height inconsistency between light and dark modes
- Environment variables being overwritten by CLI argument defaults

### 🎨 Design

- Sleek black background with blue accents (Apple + Vercel inspired)
- Glassmorphism effects with backdrop blur
- Consistent navbar across all pages (72px min-height)
- Responsive theme toggle with system preference detection
- Updated color scheme from purple to blue gradients

### 📚 Documentation

- Added comprehensive Docker deployment guide in README
- Documented Nginx fallback behavior for on-demand thumbnail generation
- Added performance benefits comparison

---

## 0.0.1

### 🏭 Added

- 2025-05-10 | adds screenshots
- 2025-05-10 | Adds static folder, change html templates to use static folder for css and image assets
- 2025-05-10 | Adds changelog, prepares for release
- 2025-05-10 | Adds main entry point and a powershell shortcut
- 2025-05-10 | Adds media module to handle thumbnail generation and file scanning utilities
- 2025-05-10 | Adds utils module with original functions from gallery.py
- 2025-05-10 | Adds flask routes module with our app's routes
- 2025-05-10 | Adds config.py to encapsulate all configuration functions
- 2025-05-10 | Adds new module and app.py to separate concerns
- 2025-05-10 | Adds gallery templates
- 2025-05-10 | Added initial gallery.py


### 💡 Fixed

- 2025-05-10 | Fix the entry point documentation in README


### 🖌️ Various

- 2025-05-10 | Updates readme with all comamnd usage after the refactoring
- 2025-05-10 | Initial commit



---
Changelog as of 5/10/2025.