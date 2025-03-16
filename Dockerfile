# Use official Python base image with build tools
FROM python:3.10-slim

# Install system dependencies for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libmupdf-dev \
    mupdf \
    libgl1 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (App Runner will use PORT env var)
EXPOSE 8000

# Run with dynamic port configuration
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
