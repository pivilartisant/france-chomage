#!/bin/bash
set -e

echo "🚂 Starting France Chômage Bot on Railway (Safe Deployment)..."

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

# Test database connection
echo "🔍 Testing database connection..."
python -c "
import os
import asyncio
from france_chomage.database import connection
from sqlalchemy import text

async def test_connection():
    try:
        connection.initialize_database()
        if connection.engine is None:
            raise RuntimeError('Database engine not initialized')
        
        async with connection.engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            print('✅ Database connection successful')
            return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

try:
    success = asyncio.run(test_connection())
    if not success:
        exit(1)
except Exception as e:
    print(f'❌ Database test failed: {e}')
    exit(1)
"

# Check if this is first deployment or migration needed
echo "🔍 Checking database state..."
python -c "
import asyncio
from france_chomage.database import connection
from sqlalchemy import text

async def check_first_deployment():
    connection.initialize_database()
    async with connection.engine.begin() as conn:
        try:
            # Check if jobs table exists
            result = await conn.execute(
                text('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\' AND tablename = \\'jobs\\';')
            )
            tables = [row[0] for row in result]
            
            if 'jobs' not in tables:
                print('🆕 First deployment - will create initial schema')
                with open('/tmp/first_deployment', 'w') as f:
                    f.write('true')
            else:
                # Check if we have existing data
                result = await conn.execute(text('SELECT COUNT(*) FROM jobs;'))
                job_count = result.scalar()
                print(f'📊 Existing deployment - found {job_count} jobs in database')
                with open('/tmp/first_deployment', 'w') as f:
                    f.write('false')
        except Exception as e:
            print(f'❌ Error checking database state: {e}')
            exit(1)

try:
    asyncio.run(check_first_deployment())
except Exception as e:
    print(f'❌ Database state check failed: {e}')
    exit(1)
"

# Read the deployment state
FIRST_DEPLOYMENT=$(cat /tmp/first_deployment)

if [ "$FIRST_DEPLOYMENT" = "true" ]; then
    echo "🆕 First deployment detected - creating initial database schema..."
    
    # Create tables using SQLAlchemy models
    python -c "
import asyncio
from france_chomage.database.models import Base
from france_chomage.database import connection

async def create_initial_schema():
    connection.initialize_database()
    async with connection.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Initial database schema created')

try:
    asyncio.run(create_initial_schema())
except Exception as e:
    print(f'❌ Schema creation failed: {e}')
    exit(1)
"
    
    # Stamp database as being at head revision
    echo "🔖 Marking database as up-to-date with migrations..."
    python -m france_chomage migrate stamp head
    
else
    echo "🔄 Existing deployment - checking for pending migrations..."
    
    # Check if migrations are needed
    if python -m france_chomage migrate check; then
        echo "✅ Database is up to date"
    else
        echo "⚠️ Database needs migration - applying pending migrations..."
        python -m france_chomage migrate upgrade
    fi
fi

# Final verification with delay
echo "🔍 Final database verification..."
echo "⏳ Waiting 5 seconds before verification..."
sleep 5

python -c "
import asyncio
from france_chomage.database import connection
from sqlalchemy import text

async def verify_database():
    connection.initialize_database()
    async with connection.engine.begin() as conn:
        result = await conn.execute(text('SELECT COUNT(*) FROM jobs;'))
        job_count = result.scalar()
        print(f'✅ Database ready - {job_count} jobs in database')

try:
    asyncio.run(verify_database())
except Exception as e:
    print(f'⚠️ Database verification failed: {e}')
    print('✅ Continuing with scheduler startup...')
"

echo "📊 Database status:"
echo "⏭️ Skipping detailed status check to avoid connection conflicts with scheduler"

echo "🚀 Starting scheduler..."
exec "$@"
