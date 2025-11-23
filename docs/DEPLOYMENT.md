# Deployment Guide - Py Home Gallery

## Overview

This guide covers deploying Py Home Gallery in production using Docker and Nginx. The Docker setup provides optimal performance by using Nginx to serve static files while Flask handles API requests and dynamic content.

## Docker Deployment

### Architecture

The Docker deployment consists of two containers:

1. **Gallery Container**: Flask application with Waitress WSGI server
2. **Nginx Container**: Reverse proxy and static file server

```
┌─────────────────────────────────────┐
│         Client Request              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Nginx Container             │
│  ┌──────────────────────────────┐   │
│  │  Static Files (media/thumbs) │   │
│  │  → Serve directly            │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  API Requests                │   │
│  │  → Proxy to Flask            │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Gallery Container (Flask)      │
│  ┌──────────────────────────────┐   │
│  │  API Endpoints               │   │
│  │  Thumbnail Generation        │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Quick Start

1. **Create environment file**:

```bash
# Create .env file
cat > .env << EOF
MEDIA_DIR=/path/to/your/media
THUMBNAIL_DIR=/path/to/your/thumbnails
HOST_PORT=8000
WORKER_THREADS=2
EOF
```

2. **Build and run**:

```bash
docker-compose up -d
```

3. **Access the gallery**:

Open `http://localhost:8000` (or your configured port)

### Docker Compose Configuration

The `docker-compose.yml` file defines both services:

```yaml
version: '3.8'

services:
  gallery:
    build: .
    container_name: py-home-gallery
    expose:
      - "5000"  # Internal port only
    volumes:
      - ${MEDIA_DIR}:/media:ro  # Read-only
      - ${THUMBNAIL_DIR}:/thumbnails
      - ./logs:/app/logs
    environment:
      - PY_HOME_GALLERY_MEDIA_DIR=/media
      - PY_HOME_GALLERY_THUMB_DIR=/thumbnails
      - PY_HOME_GALLERY_HOST=0.0.0.0
      - PY_HOME_GALLERY_PORT=5000
      - PY_HOME_GALLERY_PRODUCTION=true
      - PY_HOME_GALLERY_SERVE_MEDIA=false
      - PY_HOME_GALLERY_CACHE_ENABLED=true
      - PY_HOME_GALLERY_CACHE_TTL=300
      - PY_HOME_GALLERY_WORKER_ENABLED=true
      - PY_HOME_GALLERY_WORKER_THREADS=2
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000')"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: py-home-gallery-nginx
    ports:
      - "${HOST_PORT:-8000}:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ${MEDIA_DIR}:/media:ro
      - ${THUMBNAIL_DIR}:/thumbnails:ro
    depends_on:
      - gallery
    restart: unless-stopped
```

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Required: Path to your media files
MEDIA_DIR=/path/to/your/media

# Required: Path for generated thumbnails
THUMBNAIL_DIR=/path/to/your/thumbnails

# Optional: Host port (default: 8000)
HOST_PORT=8000

# Optional: Number of worker threads (default: 2)
WORKER_THREADS=2

# Optional: Cache TTL in seconds (default: 300)
CACHE_TTL=300

# Optional: Log level (default: INFO)
LOG_LEVEL=INFO
```

### Dockerfile

The Dockerfile builds the application image:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir waitress

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /media /thumbnails

# Expose internal port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]
```

### Nginx Configuration

Nginx serves static files and proxies API requests to Flask:

```nginx
server {
    listen 80;
    
    # Serve media files directly
    location /media/ {
        alias /media/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    # Serve thumbnails directly
    location /thumbnails/ {
        alias /thumbnails/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy API requests to Flask
    location / {
        proxy_pass http://gallery:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Key Features**:
- Static files served directly by Nginx (faster)
- API requests proxied to Flask
- Cache headers for static content
- Automatic fallback to Flask for missing thumbnails

## Deployment Steps

### 1. Prepare Directories

```bash
# Create directories
mkdir -p /path/to/media
mkdir -p /path/to/thumbnails
mkdir -p /path/to/logs

# Set permissions
chmod 755 /path/to/media
chmod 755 /path/to/thumbnails
```

### 2. Configure Environment

Create `.env` file with your paths:

```bash
MEDIA_DIR=/path/to/media
THUMBNAIL_DIR=/path/to/thumbnails
HOST_PORT=8000
```

### 3. Build and Start

```bash
# Build images
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Deployment

```bash
# Check container status
docker-compose ps

# Check health
curl http://localhost:8000

# View logs
docker-compose logs gallery
docker-compose logs nginx
```

## Docker Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gallery
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 gallery
```

### Stop and Start

```bash
# Stop containers
docker-compose stop

# Start containers
docker-compose start

# Restart containers
docker-compose restart

# Stop and remove containers
docker-compose down
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose build gallery
docker-compose up -d gallery
```

### Access Container Shell

```bash
# Gallery container
docker exec -it py-home-gallery bash

# Nginx container
docker exec -it py-home-gallery-nginx sh
```

### Check Environment Variables

```bash
docker exec py-home-gallery env | grep PY_HOME_GALLERY
```

## Production Considerations

### Security

1. **Read-only mounts**: Media directory mounted as read-only
2. **Network isolation**: Containers communicate internally
3. **Health checks**: Automatic health monitoring
4. **Restart policy**: Containers restart automatically

### Performance

1. **Nginx static serving**: 3-5x faster than Flask
2. **Cache headers**: Browser caching for static files
3. **Worker threads**: Parallel thumbnail generation
4. **Cache system**: Reduced filesystem I/O

### Monitoring

1. **Health checks**: Automatic container health monitoring
2. **Logs**: Centralized logging via Docker
3. **Metrics**: Monitor container resource usage

```bash
# Container stats
docker stats

# Health check status
docker inspect py-home-gallery | grep Health
```

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   docker-compose logs gallery
   ```

2. **Check environment variables**:
   ```bash
   docker exec py-home-gallery env
   ```

3. **Check volume mounts**:
   ```bash
   docker inspect py-home-gallery | grep Mounts
   ```

### Nginx 502 Bad Gateway

1. **Check Flask container**:
   ```bash
   docker-compose ps gallery
   docker-compose logs gallery
   ```

2. **Check network**:
   ```bash
   docker network ls
   docker network inspect py-home-gallery_default
   ```

3. **Test Flask directly**:
   ```bash
   docker exec py-home-gallery curl http://localhost:5000
   ```

### Media Files Not Accessible

1. **Check volume mounts**:
   ```bash
   docker inspect py-home-gallery | grep Mounts
   ```

2. **Check permissions**:
   ```bash
   docker exec py-home-gallery ls -la /media
   ```

3. **Check Nginx config**:
   ```bash
   docker exec py-home-gallery-nginx nginx -t
   ```

### Thumbnails Not Generating

1. **Check worker status**:
   ```bash
   docker-compose logs gallery | grep worker
   ```

2. **Check FFmpeg**:
   ```bash
   docker exec py-home-gallery ffmpeg -version
   ```

3. **Check thumbnail directory**:
   ```bash
   docker exec py-home-gallery ls -la /thumbnails
   ```

## Advanced Configuration

### Custom Nginx Configuration

Create custom `nginx.conf`:

```nginx
# Custom nginx.conf
server {
    listen 80;
    server_name gallery.example.com;
    
    # ... your custom configuration ...
}
```

Mount in `docker-compose.yml`:

```yaml
volumes:
  - ./custom-nginx.conf:/etc/nginx/nginx.conf:ro
```

### SSL/HTTPS

Add SSL configuration to Nginx:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    # ... rest of configuration ...
}
```

Mount certificates:

```yaml
volumes:
  - ./ssl/cert.pem:/etc/ssl/certs/cert.pem:ro
  - ./ssl/key.pem:/etc/ssl/private/key.pem:ro
```

### Resource Limits

Set resource limits in `docker-compose.yml`:

```yaml
services:
  gallery:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Non-Docker Deployment

### Direct Python Deployment

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install waitress
   ```

2. **Run with Waitress**:
   ```bash
   waitress-serve --host=0.0.0.0 --port=8000 --call py_home_gallery:create_app
   ```

3. **Or use run.py**:
   ```bash
   python run.py --production
   ```

### Systemd Service

Create `/etc/systemd/system/py-home-gallery.service`:

```ini
[Unit]
Description=Py Home Gallery
After=network.target

[Service]
Type=simple
User=gallery
WorkingDirectory=/opt/py-home-gallery
Environment="PY_HOME_GALLERY_MEDIA_DIR=/media"
Environment="PY_HOME_GALLERY_PORT=8000"
ExecStart=/usr/bin/python3 /opt/py-home-gallery/run.py --production
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable py-home-gallery
sudo systemctl start py-home-gallery
```

## Related Documentation

- [Configuration Guide](CONFIGURATION.md) - Configuration options
- [Cache and Workers Guide](CACHE_AND_WORKERS.md) - Performance tuning
- [Security Guide](SECURITY.md) - Security best practices

---

**Last Updated**: December 2024  
**Project Version**: 0.2.0

