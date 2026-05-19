# Use the official Python 3.10-slim image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy all project directories and files (frontend, backend, scripts, models, etc.)
COPY . .

# Expose port 8000 for access
EXPOSE 8000

# Set PYTHONPATH so absolute package imports like 'backend.routes...' resolve properly
ENV PYTHONPATH=/app

# Start the application using Uvicorn, binding to all interfaces
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
