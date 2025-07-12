FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Force Python to show logs immediately
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING=UTF-8

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

# Health check
HEALTHCHECK --interval=300s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "from france_chomage.config import settings; print('Health check OK')" || exit 1

# Default command - nouvelle architecture v2.0
CMD ["python", "-m", "france_chomage", "scheduler"]
