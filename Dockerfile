# Safety Net Dockerfile for Render Root
# This allows the backend to be deployed even if paths are misconfigured.

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Create uploads directory
RUN mkdir -p uploads

# Default port for Backend
EXPOSE 8000

# Run uvicorn with Render's dynamic port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
