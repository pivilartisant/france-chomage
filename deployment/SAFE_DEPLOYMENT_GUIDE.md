# Safe Deployment Guide

## Problem Fixed

The original deployment script was **destructively dropping tables** on every deployment:
```bash
# OLD - DESTRUCTIVE
await conn.execute(text('DROP TABLE IF EXISTS jobs CASCADE;'))
```

This caused **data loss** on every deployment.

## Solution Implemented

### 1. Safe Railway Deployment
- ✅ **Removed destructive DROP TABLE commands**
- ✅ **Added proper database state checking**
- ✅ **Implemented safe table creation** (only if needed)
- ✅ **Added data preservation logic**

### 2. Migration Management
- ✅ **Added Alembic migration commands** (`france_chomage migrate`)
- ✅ **Created migration checking** before deployment
- ✅ **Added database backup functionality**

### 3. New CLI Commands

#### Database Management
```bash
# Backup database before deployment
python -m france_chomage db backup

# Check database status
python -m france_chomage db status

# Initialize database (first time only)
python -m france_chomage db init
```

#### Migration Management
```bash
# Check if migrations are needed
python -m france_chomage migrate check

# Apply pending migrations
python -m france_chomage migrate upgrade

# Create new migration
python -m france_chomage migrate revision -m "Add new column"

# Show migration history
python -m france_chomage migrate history
```

## Updated Files

### Modified Files
- `deployment/railway/railway-entrypoint.sh` - Removed destructive commands
- `france_chomage/cli/database.py` - Added backup functionality
- `france_chomage/cli/__init__.py` - Added migration CLI

### New Files
- `deployment/railway/safe-railway-entrypoint.sh` - Safe deployment script
- `france_chomage/cli/migration.py` - Alembic migration management
- `deployment/SAFE_DEPLOYMENT_GUIDE.md` - This guide

## How to Use

### Option 1: Use Updated Script (Recommended)
The existing `railway-entrypoint.sh` has been updated to be safe. No action needed.

### Option 2: Use New Safe Script
Update your Railway deployment to use the new safe script:

```dockerfile
# In Dockerfile, change from:
COPY deployment/railway/railway-entrypoint.sh /railway-entrypoint.sh

# To:
COPY deployment/railway/safe-railway-entrypoint.sh /railway-entrypoint.sh
```

### Before Deployment (Recommended)
```bash
# 1. Backup your database
python -m france_chomage db backup

# 2. Check migration status
python -m france_chomage migrate check

# 3. Apply migrations if needed
python -m france_chomage migrate upgrade
```

## What Changed in Deployment

### Before (Destructive)
```bash
# OLD - Data loss on every deployment
DROP TABLE IF EXISTS jobs CASCADE;
CREATE TABLE jobs (...);
```

### After (Safe)
```bash
# NEW - Preserves existing data
if table_exists('jobs'):
    print('✅ Table exists - preserving data')
    apply_migrations_if_needed()
else:
    print('🆕 Creating initial schema')
    create_tables()
```

## Migration Strategy

1. **First Deployment**: Creates initial schema
2. **Subsequent Deployments**: Checks for migrations, applies if needed
3. **Data Preservation**: Never drops existing tables
4. **Backup Support**: Easy database backups before changes

## Testing

```bash
# Test database connection
python -c "from france_chomage.database import connection; connection.initialize_database()"

# Test migration status
python -m france_chomage migrate check

# Test backup functionality
python -m france_chomage db backup --category communication
```

## Rollback Strategy

If something goes wrong:

1. **Restore from backup**:
   ```bash
   python -m france_chomage db migrate --json-file backup_jobs_communication_20240101_120000.json
   ```

2. **Downgrade migrations**:
   ```bash
   python -m france_chomage migrate downgrade <previous_revision>
   ```

3. **Check database state**:
   ```bash
   python -m france_chomage db status
   ```

## Security Improvements

- ✅ **No more data loss** on deployments
- ✅ **Proper migration tracking** with Alembic
- ✅ **Backup functionality** before changes
- ✅ **Database state verification** before operations
- ✅ **Safe error handling** during deployment

Your data is now **safe** across deployments! 🎉
