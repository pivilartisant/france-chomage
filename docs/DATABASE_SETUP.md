# Database Setup Guide

## Environment Variables

Add these variables to your `.env` file for database configuration:

```env
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/france_chomage

# OR use individual components:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=france_chomage
DB_USER=postgres
DB_PASSWORD=postgres

# Optional: Enable SQL query logging
DB_ECHO=false
```

## Quick Setup Commands

1. **Initialize database (create tables)**:
   ```bash
   make db-init
# or
python -m france_chomage db init
   ```

2. **Migrate existing JSON data** (if migrating from old system):
   ```bash
   make db-migrate
# or
python -m france_chomage db migrate
   ```

3. **Check database status**:
   ```bash
   make db-status
# or
python -m france_chomage db status
   ```

## PostgreSQL Required

PostgreSQL is required for the application to function. The system no longer uses JSON files for storage. Install PostgreSQL using your system's package manager or download from https://postgresql.org/download/.

## SQLite Alternative (Future)

For simpler setups, we could add SQLite support:
```env
DATABASE_URL=sqlite+aiosqlite:///./france_chomage.db
```

## Full Workflow

After database setup, the improved workflow is:

1. **Scraping**: `python -m france_chomage scrape communication`
   - Scrapes jobs from sites
   - Filters jobs to last 30 days only
   - Removes duplicates automatically
   - Saves to database

2. **Sending**: `python -m france_chomage send communication`
   - Loads unsent jobs from database (last 30 days)
   - Sends to Telegram with dd/mm/yyyy date format
   - Marks jobs as sent in database

3. **Complete workflow**: `python -m france_chomage workflow communication`
   - Combines scraping + sending
   - Only sends NEW jobs since last run

## Benefits

- ✅ **No more duplicates**: Jobs are deduplicated across runs
- ✅ **30-day filtering**: Only recent, relevant jobs
- ✅ **Better date format**: dd/mm/yyyy in Telegram messages
- ✅ **Incremental updates**: Only new jobs are sent
- ✅ **Data persistence**: Jobs stored reliably in database
- ✅ **Performance**: Faster queries with proper indexing
