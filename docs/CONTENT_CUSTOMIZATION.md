# Content Customization Guide

Py Home Gallery supports comprehensive content customization, allowing you to tailor all text strings, labels, and descriptions to match your specific use case - whether it's a wedding gallery, family photo collection, event documentation, or any other themed media collection.

## Overview

All user-facing text in the application can be customized through a single `content.json` file. This includes:

- Site title and branding
- Navigation labels
- Page titles and descriptions
- Button labels and icons
- Stats labels
- Loading messages
- And more!

## Quick Start

1. **Copy the example file:**
   ```bash
   cp content.json.example content.json
   ```

2. **Edit `content.json`** with your custom text
3. **Restart the application** to see your changes

That's it! No code changes required.

## Configuration Methods

### Method 1: Environment Variable (Recommended for Docker)

Set content directly as a JSON string in an environment variable - perfect for Docker deployments:

**Bash/Linux/macOS:**
```bash
export PY_HOME_GALLERY_CONTENT_JSON='{"site":{"title":"Our Wedding"},"home":{"hero_title":"Our Special Day"}}'
python run.py --media-dir /path/to/media
```

**Docker (.env file):**
```env
CONTENT_JSON='{"site":{"title":"Sarah & John Wedding"},"home":{"hero_title":"Our Special Day","hero_subtitle":"June 15, 2024"},"navigation":{"site_name":"Our Wedding"}}'
```

Then:
```bash
docker-compose up -d
```

**Benefits:**
- No need for separate content.json file
- Easy to version control in .env
- Perfect for Docker/container deployments
- Can be set in CI/CD pipelines

### Method 2: File in Default Location

Place `content.json` in the project root directory (same location as `run.py`):

```
py-home-gallery/
├── content.json          # Your custom content
├── content.json.example  # Template with examples
├── run.py
└── ...
```

### Method 3: Custom File Location

Specify a custom path using the `--content-path` argument or environment variable:

**Command Line:**
```bash
python run.py --content-path "/path/to/custom/content.json"
```

**Environment Variable:**
```bash
export PY_HOME_GALLERY_CONTENT_PATH="/path/to/custom/content.json"
python run.py
```

**Docker (.env file):**
```env
CONTENT_PATH=/path/to/content.json
```

### Priority Order

Content is loaded in this priority order (first found wins):
1. `PY_HOME_GALLERY_CONTENT_JSON` environment variable
2. File specified by `--content-path` or `PY_HOME_GALLERY_CONTENT_PATH`
3. `content.json` in current directory
4. `content.json` in project root
5. Default content (built-in)

## Content Structure

The `content.json` file is organized into logical sections:

```json
{
  "site": {
    "title": "Your Gallery Name",
    "description": "Your gallery description"
  },
  "navigation": {
    "logo_alt": "Logo",
    "site_name": "Your Site Name"
  },
  "home": {
    "hero_title": "Welcome Title",
    "hero_subtitle": "Welcome message",
    "stats": {
      "total_files": "Label for total files",
      "images": "Label for images",
      "videos": "Label for videos",
      "folders": "Label for folders"
    }
  },
  "views": {
    "browse": {
      "title": "Browse",
      "description": "Browse description",
      "icon": "📂"
    }
    // ... more views
  }
}
```

### Partial Customization

You don't need to specify all fields - only customize what you want to change. Any missing fields will use the default values automatically.

**Example - Minimal customization:**
```json
{
  "site": {
    "title": "Our Wedding Photos"
  },
  "home": {
    "hero_title": "Sarah & John's Wedding",
    "hero_subtitle": "June 15, 2024"
  }
}
```

## Use Case Examples

### Wedding Gallery

Create an elegant wedding photo gallery:

```json
{
  "site": {
    "title": "Sarah & John's Wedding",
    "description": "Wedding Photos & Videos - June 15, 2024"
  },
  "navigation": {
    "site_name": "Our Wedding"
  },
  "home": {
    "hero_title": "Our Special Day",
    "hero_subtitle": "Celebrating love, laughter, and happily ever after",
    "stats": {
      "total_files": "Total Memories",
      "images": "Photos",
      "videos": "Videos",
      "folders": "Collections"
    }
  },
  "views": {
    "browse": {
      "title": "Collections",
      "description": "Browse photos by event (ceremony, reception, etc.)",
      "icon": "💍"
    },
    "gallery": {
      "title": "All Photos",
      "description": "View all wedding photos in one place",
      "icon": "📸"
    },
    "newest": {
      "title": "Latest",
      "description": "Recently added photos from guests",
      "icon": "✨"
    }
  }
}
```

### Family Photo Collection

```json
{
  "site": {
    "title": "The Smith Family Photos",
    "description": "Our family memories from 2010-2024"
  },
  "home": {
    "hero_title": "Family Memories",
    "hero_subtitle": "A collection of our precious moments together",
    "stats": {
      "total_files": "Total Memories",
      "images": "Photos",
      "videos": "Videos",
      "folders": "Years"
    }
  },
  "views": {
    "browse": {
      "title": "Browse by Year",
      "description": "Navigate through our family timeline",
      "icon": "📅"
    },
    "shuffle": {
      "title": "Memory Lane",
      "description": "Take a random walk through our memories",
      "icon": "🎲"
    }
  }
}
```

### Corporate Event Gallery

```json
{
  "site": {
    "title": "Tech Summit 2024",
    "description": "Conference Photos, Presentations & Videos"
  },
  "home": {
    "hero_title": "Tech Summit 2024",
    "hero_subtitle": "Innovation, Inspiration, and Ideas",
    "stats": {
      "total_files": "Total Assets",
      "images": "Photos",
      "videos": "Presentations",
      "folders": "Sessions"
    }
  },
  "views": {
    "browse": {
      "title": "Sessions",
      "description": "Browse by conference session",
      "icon": "🎤"
    },
    "gallery": {
      "title": "Photo Gallery",
      "description": "All event photography",
      "icon": "📷"
    }
  }
}
```

### Travel/Vacation Gallery

```json
{
  "site": {
    "title": "Europe Trip 2024",
    "description": "Our amazing European adventure"
  },
  "home": {
    "hero_title": "European Adventure",
    "hero_subtitle": "Exploring the beauty of Europe - Summer 2024",
    "stats": {
      "total_files": "Trip Photos",
      "images": "Pictures",
      "videos": "Videos",
      "folders": "Destinations"
    }
  },
  "views": {
    "browse": {
      "title": "Destinations",
      "description": "Browse by country/city",
      "icon": "🗺️"
    },
    "shuffle": {
      "title": "Surprise Me",
      "description": "Random highlight from our journey",
      "icon": "✈️"
    }
  }
}
```

## Customizable Fields Reference

### Site Section
| Field | Description | Default |
|-------|-------------|---------|
| `site.title` | Browser tab title and site name | "Py Home Gallery" |
| `site.description` | Site description (meta tag) | "A lightweight media gallery..." |

### Navigation Section
| Field | Description | Default |
|-------|-------------|---------|
| `navigation.logo_alt` | Alt text for logo image | "Logo" |
| `navigation.site_name` | Site name shown in navigation | "Py Home Gallery" |

### Home Page Section
| Field | Description | Default |
|-------|-------------|---------|
| `home.hero_title` | Main heading on home page | "Your Media Collection" |
| `home.hero_subtitle` | Subtitle below main heading | "Browse, discover, and enjoy..." |
| `home.stats.total_files` | Label for total files count | "Total Files" |
| `home.stats.images` | Label for images count | "Images" |
| `home.stats.videos` | Label for videos count | "Videos" |
| `home.stats.folders` | Label for folders count | "Folders" |

### View Cards Section
Each view (`browse`, `gallery`, `shuffle`, `newest`, `infinite`) has:

| Field | Description | Example |
|-------|-------------|---------|
| `views.{view}.title` | Card title | "Browse" |
| `views.{view}.description` | Card description | "Navigate through..." |
| `views.{view}.icon` | Emoji icon for card | "📂" |

### Gallery Page Section
| Field | Description | Default |
|-------|-------------|---------|
| `gallery_page.title` | Gallery page title | "Gallery" |
| `gallery_page.all_folders` | Dropdown option for all folders | "All Folders" |
| `gallery_page.all_media` | Filter option for all media | "All Media" |
| `gallery_page.images_only` | Filter option for images only | "Images Only" |
| `gallery_page.videos_only` | Filter option for videos only | "Videos Only" |

### Browse Page Section
| Field | Description | Default |
|-------|-------------|---------|
| `browse_page.title` | Browse page title | "Browse Folders" |
| `browse_page.subtitle` | Browse page subtitle | "Navigate through..." |
| `browse_page.loading` | Loading message | "Loading folders..." |
| `browse_page.no_folders` | No folders message | "No folders found" |
| `browse_page.item_count.singular` | Singular form of item | "item" |
| `browse_page.item_count.plural` | Plural form of item | "items" |

## Emoji Icons

You can use any emoji as icons in the view cards. Some suggestions:

**General:**
- 📁 📂 🗂️ (folders)
- 🖼️ 📷 📸 (photos)
- 🎥 🎬 📹 (videos)
- ⭐ ✨ 💫 (featured)

**Events:**
- 💍 💒 (wedding)
- 🎂 🎉 🎊 (celebration)
- 🎓 (graduation)
- 🎤 🎭 (performance)

**Travel:**
- ✈️ 🗺️ 🌍 (travel)
- 🏖️ ⛰️ 🏔️ (destinations)
- 📸 🌅 (photography)

**Other:**
- 🎲 🔀 (random/shuffle)
- ∞ (infinite)
- 📅 📆 (calendar/timeline)
- 👨‍👩‍👧‍👦 (family)

## Testing Your Customization

1. Create or edit `content.json`
2. Restart the application:
   ```bash
   python run.py --media-dir /path/to/media
   ```
3. Open in browser and verify changes
4. If content doesn't update, check:
   - JSON syntax is valid (use a JSON validator)
   - Application restarted after changes
   - No typos in field names

## Troubleshooting

### Content Not Loading

**Check for JSON syntax errors:**
```bash
python -m json.tool content.json
```

If valid, it outputs formatted JSON. If errors, it shows line number.

**Check logs:**
```bash
tail -f logs/app.log
```

Look for messages like:
- "Loading custom content from: /path/to/content.json"
- "Custom content loaded successfully"
- "Error loading content from..."

### Partial Content Loading

If only some fields update, ensure your JSON structure matches the expected format. Use `content.json.example` as a reference.

### Special Characters

For special characters (quotes, apostrophes), escape them properly:

```json
{
  "home": {
    "hero_title": "Sarah & John's Wedding",
    "hero_subtitle": "A day we'll never forget"
  }
}
```

## Advanced: Programmatic Access

Developers can access content programmatically:

```python
from py_home_gallery.utils.content import get_content

# Get all content
all_content = get_content()

# Get specific value
site_title = get_content('site.title')

# Get with default fallback
custom_label = get_content('custom.label', default='Default Label')
```

## Best Practices

1. **Keep a backup:** Save your original `content.json` before making major changes
2. **Test incrementally:** Make small changes and test before continuing
3. **Use the example:** Reference `content.json.example` for proper structure
4. **Validate JSON:** Use online JSON validators to catch syntax errors
5. **Be consistent:** Maintain consistent tone and style across all text
6. **Consider length:** Very long titles/descriptions may not display well on mobile

## Related Documentation

- [Configuration Guide](CONFIGURATION.md) - All configuration options
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Development Guide](DEVELOPMENT.md) - Developer information

---

**Last Updated:** December 2024
**Version:** 0.2.0
