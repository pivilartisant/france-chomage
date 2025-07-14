#!/bin/bash
set -e

echo "🚂 Starting France Chômage Bot on Railway..."

# Check if DATABASE_URL is provided by Railway
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not found. Please add PostgreSQL service in Railway dashboard."
    exit 1
fi

echo "✅ Database URL found: ${DATABASE_URL:0:30}..."

# Railway provides DATABASE_URL in different format, ensure it's async
if [[ $DATABASE_URL == postgres://* ]]; then
    export DATABASE_URL="${DATABASE_URL/postgres:\/\//postgresql+asyncpg:\/\/}"
    echo "🔧 Converted DATABASE_URL to async format"
fi

# Wait a moment for database to be fully ready
echo "⏳ Waiting for database connection..."
sleep 5

# Initialize database tables
echo "🔧 Initializing database tables..."
python -m france_chomage db-init

# Check migration status
echo "📊 Checking database status..."
python -m france_chomage db-status

echo "🚀 Starting scheduler..."
exec "$@"
