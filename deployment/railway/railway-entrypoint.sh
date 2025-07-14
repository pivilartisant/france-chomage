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

# First, try to drop existing table if it has wrong schema
python -c "
import asyncio
from france_chomage.database.connection import initialize_database, engine
from sqlalchemy import text

async def check_and_drop():
    initialize_database()
    async with engine.begin() as conn:
        try:
            # Check if jobs table exists and has wrong schema
            result = await conn.execute(
                text('SELECT column_name FROM information_schema.columns WHERE table_name = \\'jobs\\';')
            )
            columns = [row[0] for row in result]
            print(f'📋 Existing columns: {columns}')
            
            if columns and 'title' not in columns:
                print('🔧 Table exists but has wrong schema, dropping...')
                await conn.execute(text('DROP TABLE IF EXISTS jobs CASCADE;'))
                print('✅ Old table dropped')
            elif 'title' in columns:
                print('✅ Table has correct schema')
        except Exception as e:
            print(f'📋 No existing table or error checking: {e}')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(check_and_drop())
finally:
    loop.close()
" && echo "🔧 Schema check complete"

python -m france_chomage db-init && echo "✅ db-init successful" || {
    echo "❌ db-init failed, trying direct table creation..."
    python -c "
import traceback
try:
    from france_chomage.database.migration_utils import create_tables_sync
    print('🔧 Running create_tables_sync...')
    create_tables_sync()
    print('✅ Direct table creation successful')
except Exception as e:
    print(f'❌ Direct table creation failed: {e}')
    traceback.print_exc()
    exit(1)
"
}

echo "🔍 Verifying tables and columns were created..."
python -c "
import asyncio
from france_chomage.database.connection import initialize_database, engine

async def check_tables():
    initialize_database()
    async with engine.begin() as conn:
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

from sqlalchemy import text
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
