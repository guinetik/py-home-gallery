# Py Home Gallery - Documentation

Welcome to the Py Home Gallery documentation. This documentation provides comprehensive guides for users, developers, and deployers.

## Quick Navigation

### For Users
- **[Features Guide](FEATURES.md)** - Learn about all available features and how to use them
- **[Content Customization Guide](CONTENT_CUSTOMIZATION.md)** - Customize all UI text for themed galleries
- **[Configuration Guide](CONFIGURATION.md)** - Configure the application to your needs

### For Developers
- **[Architecture](ARCHITECTURE.md)** - Understand the system architecture and design
- **[Development Guide](DEVELOPMENT.md)** - Set up your development environment and contribute
- **[API Reference](API.md)** - API endpoints and usage
- **[Type Hints](DEVELOPMENT.md#type-hints)** - Code quality and type safety

### For Deployers
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy the application in production
- **[Configuration Guide](CONFIGURATION.md)** - Production configuration options
- **[Security Guide](SECURITY.md)** - Security features and best practices

### System Documentation
- **[Logging System](LOGGING.md)** - Logging configuration and usage
- **[Error Handling](ERROR_HANDLING.md)** - Error handling strategies
- **[Cache and Workers](CACHE_AND_WORKERS.md)** - Performance features

## Documentation Structure

```
docs/
├── README.md                   # This file - documentation index
├── ARCHITECTURE.md             # System architecture and design
├── SECURITY.md                 # Security features and best practices
├── LOGGING.md                  # Logging system guide
├── ERROR_HANDLING.md           # Error handling strategies
├── CACHE_AND_WORKERS.md        # Performance features (cache & workers)
├── CONFIGURATION.md            # Configuration guide
├── CONTENT_CUSTOMIZATION.md    # Content customization guide
├── DEPLOYMENT.md               # Deployment guide
├── DEVELOPMENT.md              # Development guide for contributors
├── API.md                      # API endpoint reference
└── FEATURES.md                 # Features documentation
```

## Getting Started

### New to Py Home Gallery?

1. **Read the [Features Guide](FEATURES.md)** to understand what the application can do
2. **Check [Configuration Guide](CONFIGURATION.md)** to set up your media directory
3. **Review [Deployment Guide](DEPLOYMENT.md)** if deploying to production

### Want to Contribute?

1. **Read [Development Guide](DEVELOPMENT.md)** for setup instructions
2. **Review [Architecture](ARCHITECTURE.md)** to understand the codebase
3. **Check [API Reference](API.md)** for endpoint documentation

### Deploying to Production?

1. **Read [Deployment Guide](DEPLOYMENT.md)** for Docker setup
2. **Review [Security Guide](SECURITY.md)** for security best practices
3. **Check [Configuration Guide](CONFIGURATION.md)** for production settings

## Documentation by Role

### End Users
- **[Features Guide](FEATURES.md)** - How to use the gallery
- **[Content Customization Guide](CONTENT_CUSTOMIZATION.md)** - Customize UI text for your use case
- **[Configuration Guide](CONFIGURATION.md)** - Basic configuration

### Developers
- **[Architecture](ARCHITECTURE.md)** - System design and structure
- **[Development Guide](DEVELOPMENT.md)** - Development setup and guidelines
- **[API Reference](API.md)** - API endpoints
- **[Error Handling](ERROR_HANDLING.md)** - Error handling patterns
- **[Logging](LOGGING.md)** - Logging system usage

### System Administrators / DevOps
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Configuration Guide](CONFIGURATION.md)** - Advanced configuration
- **[Security Guide](SECURITY.md)** - Security features
- **[Cache and Workers](CACHE_AND_WORKERS.md)** - Performance tuning
- **[Logging](LOGGING.md)** - Log management

## Quick Reference

### Common Tasks

**Start the application:**
```bash
python run.py --media-dir "/path/to/media"
```

**Configure via environment variables:**
```bash
export PY_HOME_GALLERY_MEDIA_DIR="/path/to/media"
export PY_HOME_GALLERY_PORT=8080
python run.py
```

**Deploy with Docker:**
```bash
docker-compose up -d
```

**View logs:**
```bash
tail -f logs/app.log
```

### Key Configuration Options

- `--media-dir` - Media directory path
- `--thumbnail-dir` - Thumbnail storage directory
- `--port` - Server port (default: 8000)
- `--items-per-page` - Items per page (default: 50)
- `--cache-ttl` - Cache TTL in seconds (default: 300)
- `--worker-threads` - Background worker threads (default: 2)

See [Configuration Guide](CONFIGURATION.md) for complete details.

### API Endpoints

- `GET /` - Home page
- `GET /browse` - Browse folders (3D Cover Flow)
- `GET /gallery` - Gallery view
- `GET /random` - Random gallery
- `GET /new` - Newest first gallery
- `GET /infinite` - Infinite scroll view
- `GET /api/browse` - Browse API
- `GET /api/metadata/<path>` - Media metadata
- `GET /api/mosaic` - Mosaic thumbnails
- `GET /api/stats` - Statistics

See [API Reference](API.md) for complete API documentation.

## Project Overview

Py Home Gallery is a lightweight, Flask-based media gallery server designed for browsing and viewing local media collections across home networks. It features:

- **Multiple Gallery Views**: Browse, Gallery, Random, Newest, Infinite Scroll
- **3D Cover Flow**: iPod-inspired folder navigation
- **Automatic Thumbnails**: Video thumbnail generation
- **Security**: Path traversal protection and input validation
- **Performance**: Caching and background workers
- **Responsive Design**: Works on desktop, tablet, and mobile

## Additional Resources

- **Main README**: [../README.md](../README.md)
- **Changelog**: [../CHANGELOG.md](../CHANGELOG.md)
- **License**: [../LICENSE](../LICENSE)

## Contributing

If you'd like to contribute to Py Home Gallery:

1. Read the [Development Guide](DEVELOPMENT.md)
2. Review the [Architecture](ARCHITECTURE.md)
3. Check existing issues and pull requests
4. Follow the code style guidelines

## Support

For questions or issues:

1. Check the relevant documentation section
2. Review the [Configuration Guide](CONFIGURATION.md) for setup issues
3. Check [Deployment Guide](DEPLOYMENT.md) for deployment problems
4. Review logs using the [Logging Guide](LOGGING.md)

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

