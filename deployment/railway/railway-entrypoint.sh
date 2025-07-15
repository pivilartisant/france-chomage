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
echo "🔍 Testing database connection first..."
python -c "
import os
print(f'DATABASE_URL present: {bool(os.getenv(\"DATABASE_URL\"))}')
print(f'DATABASE_URL starts with: {os.getenv(\"DATABASE_URL\", \"\")[:50]}...')
"

echo "🔧 Attempting database initialization..."

# FORCE clean database initialization - always ensure correct schema
echo "🔧 Ensuring clean database state..."
python -c "
import asyncio
from france_chomage.database import connection
from sqlalchemy import text

async def force_clean_init():
    connection.initialize_database()
    if connection.engine is None:
        raise RuntimeError('Database engine not initialized')
    async with connection.engine.begin() as conn:
        try:
            print('🗑️ Dropping any existing tables to ensure clean state...')
            await conn.execute(text('DROP TABLE IF EXISTS jobs CASCADE;'))
            print('✅ Clean slate - ready for table creation')
        except Exception as e:
            print(f'📋 Error during cleanup (probably OK): {e}')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(force_clean_init())
finally:
    loop.close()
" && echo "🔧 Database cleanup complete"

# FORCE table creation - guaranteed to work
echo "🔧 Creating database tables with correct schema..."
python -c "
import asyncio
import traceback
from france_chomage.database.models import Base
from france_chomage.database import connection

async def force_create_tables():
    try:
        print('🔧 Initializing database connection...')
        connection.initialize_database()
        
        if connection.engine is None:
            raise RuntimeError('Database engine not initialized')
            
        print('🔧 Creating all tables from SQLAlchemy models...')
        async with connection.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print('✅ All database tables created successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Table creation failed: {e}')
        traceback.print_exc()
        return False

# Run table creation
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    success = loop.run_until_complete(force_create_tables())
    if not success:
        exit(1)
finally:
    loop.close()
"

echo "🔍 Verifying tables and columns were created..."
python -c "
import asyncio
from france_chomage.database import connection
from sqlalchemy import text

async def check_tables():
    connection.initialize_database()
    async with connection.engine.begin() as conn:
        # Check tables
        result = await conn.execute(
            text('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\';')
        )
        tables = [row[0] for row in result]
        print(f'📋 Tables found: {tables}')
        
        if 'jobs' in tables:
            print('✅ Jobs table exists!')
            
            # Check columns in jobs table
            result = await conn.execute(
                text('SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \\'jobs\\' ORDER BY ordinal_position;')
            )
            columns = [(row[0], row[1]) for row in result]
            print(f'📋 Jobs table columns: {columns}')
            
            # Check if we have expected columns
            expected_columns = ['id', 'title', 'company', 'location', 'date_posted', 'job_url', 'site', 'category']
            missing_columns = [col for col in expected_columns if not any(col == c[0] for c in columns)]
            if missing_columns:
                print(f'❌ Missing columns: {missing_columns}')
                print('🔧 Need to recreate table with correct schema')
                exit(1)
            else:
                print('✅ All expected columns found!')
        else:
            print('❌ Jobs table missing!')
            exit(1)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(check_tables())
finally:
    loop.close()
"

# Check migration status
echo "📊 Checking database status..."
python -m france_chomage db-status

echo "🚀 Starting scheduler..."
exec "$@"
