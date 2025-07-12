FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Force Python to show logs immediately
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for jobspy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Default command (can be overridden)
CMD ["python", "-u", "scheduler.py"]
