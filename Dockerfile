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

# Create directories for media and thumbnails (will be mounted as volumes)
RUN mkdir -p /media /thumbnails

# Expose internal port (Nginx will proxy to this)
EXPOSE 5000

# Set environment variables with defaults
ENV PY_HOME_GALLERY_MEDIA_DIR=/media \
    PY_HOME_GALLERY_THUMB_DIR=/thumbnails \
    PY_HOME_GALLERY_HOST=0.0.0.0 \
    PY_HOME_GALLERY_PORT=5000 \
    PY_HOME_GALLERY_PRODUCTION=true \
    PY_HOME_GALLERY_SERVE_MEDIA=false

# Run the application in production mode
CMD ["python", "run.py"]
