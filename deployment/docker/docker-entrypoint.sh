#!/bin/bash
set -e

echo "🐳 Starting France Chômage Bot with Database Support..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h db -p 5432 -U postgres; do
    echo "🔄 PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Initialize database tables if needed
echo "🔧 Initializing database tables..."
python -m france_chomage db init

# Check if we need to migrate existing data
echo "📊 Checking migration status..."
python -m france_chomage db status

echo "🚀 Starting application..."
exec "$@"
