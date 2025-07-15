FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Force Python to show logs immediately
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING=UTF-8

# Database configuration for Docker environment
ENV DOCKER_ENV=true
ENV DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/france_chomage

# Install system dependencies needed for jobspy and PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Database initialization scripts
COPY deployment/docker/docker-entrypoint.sh /docker-entrypoint.sh
COPY deployment/railway/railway-entrypoint.sh /railway-entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /docker-entrypoint.sh /railway-entrypoint.sh

# Health check - includes database connectivity
HEALTHCHECK --interval=300s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "from france_chomage.config import settings; from france_chomage.database import job_manager; print('Health check OK')" || exit 1

# Default command - Use universal entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "france_chomage", "scheduler"]
