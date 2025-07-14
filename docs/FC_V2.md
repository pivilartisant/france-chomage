# 🚀 France Chômage Bot V2.0 - Complete Upgrade Guide

## 📋 Table of Contents
1. [What's New in V2.0](#whats-new-in-v20)
2. [Technical Changes Made](#technical-changes-made)
3. [Local Testing Guide](#local-testing-guide)
4. [Production Deployment Guide](#production-deployment-guide)
5. [Database Visualization](#database-visualization)
6. [Troubleshooting](#troubleshooting)
7. [Migration from V1.0](#migration-from-v10)

---

## 🎯 What's New in V2.0

### 🗄️ **Database-Powered Architecture**
- **PostgreSQL storage** instead of JSON files
- **Automatic deduplication** across scraping sessions
- **30-day filtering** - only fresh, relevant jobs
- **Incremental updates** - only new jobs sent to Telegram
- **Data persistence** and reliability

### 📅 **Enhanced User Experience**
- **French date format** (dd/mm/yyyy) in Telegram messages
- **No duplicate jobs** - intelligent filtering
- **Fresh content only** - jobs from last 30 days
- **Better performance** with database indexing

### 🚀 **Deployment Improvements**
- **Railway one-click deploy** - easiest cloud deployment
- **Docker Compose** - complete local development stack
- **Environment detection** - automatic configuration
- **Health monitoring** - built-in checks and restart policies

---

## 🔧 Technical Changes Made

### 1. **Database Layer Implementation**

#### **New Files Created:**
```
france_chomage/database/
├── __init__.py              # Module exports
├── models.py               # SQLAlchemy database models
├── connection.py           # Async database connection
├── repository.py           # Data access layer
├── manager.py              # High-level job management
└── migration_utils.py      # JSON to DB migration tools
```

#### **Database Model (PostgreSQL):**
```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    date_posted DATE NOT NULL,
    job_url VARCHAR(1000) NOT NULL UNIQUE,
    site VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    salary_source VARCHAR(255),
    description TEXT,
    is_remote BOOLEAN DEFAULT FALSE,
    job_type VARCHAR(100),
    company_industry VARCHAR(255),
    experience_range VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    sent_to_telegram BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_job_url ON jobs(job_url);
CREATE INDEX idx_date_posted ON jobs(date_posted);
CREATE INDEX idx_category ON jobs(category);
CREATE INDEX idx_sent_to_telegram ON jobs(sent_to_telegram);
```

### 2. **Scraping Logic Updates**

#### **Enhanced Base Scraper:**
- **Database integration** - saves to DB + JSON backup
- **30-day filtering** - only recent jobs processed
- **Duplicate detection** - URL-based deduplication
- **Async operations** - better performance

#### **New Workflow:**
```python
# Old V1.0 workflow
scrape() → save_to_json() → load_from_json() → send_to_telegram()

# New V2.0 workflow  
scrape() → save_to_database() → get_unsent_jobs() → send_to_telegram() → mark_as_sent()
```

### 3. **Telegram Bot Enhancements**

#### **New Methods:**
- `send_jobs_from_database()` - sends only unsent jobs
- `format_job_message()` - improved date formatting (dd/mm/yyyy)
- Database model compatibility

#### **Removed Methods:**
- `send_jobs()` - replaced by database-centric approach
- JSON file loading logic

### 4. **CLI & Scheduler Updates**

#### **New Database Commands:**
```bash
python -m france_chomage db-init      # Initialize database tables
python -m france_chomage db-migrate   # Migrate JSON to database
python -m france_chomage db-status    # Show database statistics
python -m france_chomage db-cleanup   # Remove old jobs
```

#### **Updated Workflow Commands:**
- All commands now use database-first approach
- Consistent behavior across CLI and scheduler
- Better error handling and logging

### 5. **Deployment Infrastructure**

#### **Docker Enhancements:**
```dockerfile
# Multi-environment detection
ENTRYPOINT ["/bin/bash", "-c", "if [ \"$RAILWAY_ENVIRONMENT\" ]; then exec /railway-entrypoint.sh \"$@\"; else exec /entrypoint.sh \"$@\"; fi", "--"]
```

#### **Railway Integration:**
- Automatic DATABASE_URL conversion (postgres:// → postgresql+asyncpg://)
- Environment-specific initialization scripts
- One-click deploy template

#### **File Organization:**
```
deployment/
├── docker/
│   ├── docker-compose.yml    # Full stack with PostgreSQL
│   ├── docker-entrypoint.sh  # Docker initialization
│   └── init-db.sql          # Database setup
└── railway/
    ├── railway-entrypoint.sh # Railway initialization
    └── railway-template.json # One-click deploy config
```

---

## 🧪 Local Testing Guide

### Step 1: **Environment Setup**

#### **Prerequisites:**
```bash
# Install PostgreSQL
# macOS:
brew install postgresql
brew services start postgresql

# Ubuntu/Debian:
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **Create Database:**
```bash
# Create database
createdb france_chomage

# Verify connection
psql france_chomage -c "SELECT version();"
```

### Step 2: **Project Setup**

#### **Clone and Install:**
```bash
# Clone repository
git clone https://github.com/pivilartisant/france-chomage.git
cd france-chomage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### **Configure Environment:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required .env variables:**
```env
# Database (local PostgreSQL)
DATABASE_URL=postgresql+asyncpg://pivi@localhost:5432/france_chomage

# Telegram (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_GROUP_ID=your_group_id_here
TELEGRAM_COMMUNICATION_TOPIC_ID=3
TELEGRAM_DESIGN_TOPIC_ID=40
TELEGRAM_RESTAURATION_TOPIC_ID=326

# Scraping settings
RESULTS_WANTED=10
LOCATION=Paris
```

### Step 3: **Database Initialization**

#### **Initialize Database:**
```bash
# Create database tables
make db-init
# or
python -m france_chomage db-init

# Check database status
make db-status
# or  
python -m france_chomage db-status
```

#### **Migrate Existing Data (if any):**
```bash
# If you have old JSON files to migrate
make db-migrate
# or
python -m france_chomage db-migrate
```

### Step 4: **Test Scraping**

#### **Test Individual Categories:**
```bash
# Test communication jobs
python -m france_chomage scrape communication

# Check database after scraping
make db-status

# Test sending (dry run - check what would be sent)
python -m france_chomage send communication --dry-run  # (if implemented)
```

#### **Verify Database Storage:**
```bash
# Connect to database directly
psql france_chomage

# Check scraped jobs
SELECT category, COUNT(*) as job_count, MAX(date_posted) as latest_date 
FROM jobs 
GROUP BY category;

# Check unsent jobs
SELECT category, COUNT(*) as unsent_count 
FROM jobs 
WHERE sent_to_telegram = false 
GROUP BY category;

# Exit psql
\q
```

### Step 5: **Test Complete Workflow**

#### **End-to-End Test:**
```bash
# Complete workflow (scrape + send)
python -m france_chomage workflow communication

# Verify jobs were marked as sent
psql france_chomage -c "SELECT COUNT(*) FROM jobs WHERE sent_to_telegram = true;"
```

#### **Test Scheduler:**
```bash
# Test scheduler (Ctrl+C to stop)
python -m france_chomage scheduler
```

### Step 6: **Docker Testing (Optional)**

#### **Test with Docker Compose:**
```bash
# Start full stack (app + PostgreSQL)
make docker-up

# Check logs
make docker-logs

# Test database connection
make docker-admin
# Visit http://localhost:8081 (Adminer interface)

# Stop services
make docker-down
```

---

## 🚀 Production Deployment Guide

### Option 1: **Railway Deployment (Recommended)**

#### **Step 1: One-Click Deploy**
1. **Click Deploy Button:**
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

2. **Configure Environment Variables:**
   ```env
   TELEGRAM_BOT_TOKEN=your_production_bot_token
   TELEGRAM_GROUP_ID=your_production_group_id
   ```

3. **Verify Deployment:**
   - Check Railway dashboard for successful build
   - Monitor application logs
   - Verify database initialization

#### **Step 2: Manual Railway Deploy**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy project
railway up

# Check status
railway status

# View logs
railway logs
```

#### **Step 3: Database Setup on Railway**
1. **Add PostgreSQL Service:**
   - Go to Railway dashboard
   - Click "New Service" → "Database" → "PostgreSQL"
   - Railway automatically creates `DATABASE_URL`

2. **Verify Database:**
   ```bash
   # Connect to Railway database
   railway run psql $DATABASE_URL
   
   # Check tables
   \dt
   
   # Check initial data
   SELECT COUNT(*) FROM jobs;
   ```

### Option 2: **Docker Deployment (VPS/Cloud)**

#### **Step 1: Server Setup**
```bash
# On your server (Ubuntu example)
sudo apt update
sudo apt install docker.io docker-compose

# Clone repository
git clone https://github.com/pivilartisant/france-chomage.git
cd france-chomage
```

#### **Step 2: Configure Environment**
```bash
# Create production environment file
cp .env.example .env.production

# Edit with production values
nano .env.production
```

**Production .env.production:**
```env
# Database (Docker Compose provides this)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/france_chomage

# Telegram production bot
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_GROUP_ID=your_production_group_id

# Production settings
DOCKER_ENV=true
FORCE_DOCKER_MODE=1
RESULTS_WANTED=20
LOCATION=Paris
```

#### **Step 3: Deploy with Docker Compose**
```bash
# Start services
cd deployment/docker
docker-compose --env-file ../../.env.production up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Option 3: **Heroku Deployment**

#### **Step 1: Heroku Setup**
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini
```

#### **Step 2: Configure Heroku**
```bash
# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TELEGRAM_GROUP_ID=your_group_id
heroku config:set DOCKER_ENV=true
heroku config:set FORCE_DOCKER_MODE=1

# Deploy
git push heroku main
```

---

## 👁️ Database Visualization

### 1. **Command Line Interface**

#### **Basic Queries:**
```bash
# Connect to database
psql $DATABASE_URL  # or psql france_chomage for local

# Show all tables
\dt

# Basic statistics
SELECT 
    category,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN sent_to_telegram THEN 1 END) as sent_jobs,
    MAX(date_posted) as latest_job_date,
    MIN(date_posted) as oldest_job_date
FROM jobs 
GROUP BY category;

# Recent jobs (last 7 days)
SELECT title, company, location, date_posted, category 
FROM jobs 
WHERE date_posted >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date_posted DESC 
LIMIT 20;

# Unsent jobs count
SELECT category, COUNT(*) as unsent_count
FROM jobs 
WHERE sent_to_telegram = false
AND date_posted >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category;

# Job sites distribution
SELECT site, COUNT(*) as job_count
FROM jobs
GROUP BY site
ORDER BY job_count DESC;
```

### 2. **Adminer (Web Interface)**

#### **Docker Compose Setup:**
```bash
# Start with admin interface
make docker-admin
# or
cd deployment/docker && docker-compose --profile admin up -d

# Access Adminer
open http://localhost:8081
```

**Adminer Login:**
- **Server:** `db`
- **Username:** `postgres`
- **Password:** `postgres`
- **Database:** `france_chomage`

#### **Railway Database Access:**
```bash
# Get Railway database URL
railway variables

# Connect via Adminer or any PostgreSQL client
# Use the DATABASE_URL connection string
```

### 3. **pgAdmin (Advanced GUI)**

#### **Installation:**
```bash
# macOS
brew install --cask pgadmin4

# Ubuntu
sudo apt install pgadmin4
```

#### **Connection Setup:**
1. **Create Server Connection:**
   - Host: `localhost` (local) or Railway host
   - Port: `5432`
   - Database: `france_chomage`
   - Username: `postgres`
   - Password: your password

2. **Useful Queries in pgAdmin:**
```sql
-- Jobs timeline
SELECT DATE(date_posted) as date, COUNT(*) as jobs_count
FROM jobs
WHERE date_posted >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(date_posted)
ORDER BY date;

-- Success rate by category
SELECT 
    category,
    COUNT(*) as total_scraped,
    COUNT(CASE WHEN sent_to_telegram THEN 1 END) as successfully_sent,
    ROUND(COUNT(CASE WHEN sent_to_telegram THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM jobs
GROUP BY category;

-- Duplicate detection
SELECT job_url, COUNT(*) as duplicate_count
FROM jobs
GROUP BY job_url
HAVING COUNT(*) > 1;
```

### 4. **Application Built-in Stats**

#### **CLI Database Status:**
```bash
# Comprehensive database status
make db-status
# or
python -m france_chomage db-status
```

**Sample Output:**
```
==================================================
📊 DATABASE MIGRATION STATUS
==================================================

🏷️ COMMUNICATION
   Total jobs: 45
   Recent (30 days): 23
   Unsent jobs: 5
   Latest job: 15/01/2024

🏷️ DESIGN
   Total jobs: 38
   Recent (30 days): 19
   Unsent jobs: 3
   Latest job: 14/01/2024

🏷️ RESTAURATION
   Total jobs: 52
   Recent (30 days): 28
   Unsent jobs: 7
   Latest job: 15/01/2024

📈 OVERALL STATS (Last 30 days)
   Total jobs: 70
   Sent to Telegram: 55
   Pending: 15

==================================================
```

### 5. **Monitoring Queries**

#### **Performance Monitoring:**
```sql
-- Database size
SELECT 
    pg_size_pretty(pg_database_size('france_chomage')) as database_size;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public';

-- Index usage
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' AND tablename = 'jobs';
```

#### **Health Check Queries:**
```sql
-- Recent activity
SELECT 
    DATE(created_at) as date,
    COUNT(*) as jobs_added
FROM jobs
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Error detection (jobs with missing data)
SELECT COUNT(*) as jobs_with_missing_data
FROM jobs
WHERE title IS NULL 
   OR company IS NULL 
   OR job_url IS NULL;

-- Telegram sending success rate
SELECT 
    DATE(sent_at) as date,
    COUNT(*) as jobs_sent
FROM jobs
WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(sent_at)
ORDER BY date;
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### **1. Database Connection Errors**

**Error:** `Connection refused` or `Database does not exist`
```bash
# Check PostgreSQL status
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Ubuntu

# Restart PostgreSQL
brew services restart postgresql      # macOS
sudo systemctl restart postgresql     # Ubuntu

# Recreate database
dropdb france_chomage  # if exists
createdb france_chomage
```

#### **2. Migration Issues**

**Error:** `Table already exists` or migration fails
```bash
# Reset database (CAUTION: deletes all data)
python -c "
from france_chomage.database.models import Base
from france_chomage.database.connection import engine, initialize_database
import asyncio

async def reset_db():
    initialize_database()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print('Database reset complete')

asyncio.run(reset_db())
"

# Re-initialize
make db-init
```

#### **3. Telegram Bot Issues**

**Error:** `Bot token invalid` or `Chat not found`
```bash
# Test bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Test group access
python -c "
from france_chomage.config import settings
print(f'Bot token: {settings.telegram_bot_token[:10]}...')
print(f'Group ID: {settings.telegram_group_id}')
"
```

#### **4. Railway Deployment Issues**

**Error:** Build fails or app won't start
```bash
# Check Railway logs
railway logs

# Verify environment variables
railway variables

# Check database connection
railway run python -c "
from france_chomage.database.connection import get_database_url
print('Database URL configured:', bool(get_database_url()))
"
```

#### **5. Docker Issues**

**Error:** Container fails to start
```bash
# Check container logs
docker-compose logs app

# Verify database connection
docker-compose exec app python -c "
from france_chomage.database.connection import get_database_url
print(get_database_url())
"

# Restart services
docker-compose down
docker-compose up -d
```

### Performance Optimization

#### **Database Optimization:**
```sql
-- Analyze table statistics
ANALYZE jobs;

-- Vacuum to reclaim space
VACUUM jobs;

-- Re-index for performance
REINDEX TABLE jobs;
```

#### **Application Optimization:**
```bash
# Clean up old jobs (90+ days)
make db-cleanup
# or
python -m france_chomage db-cleanup --days 90

# Monitor memory usage
docker stats  # for Docker deployment
```

---

## 🔄 Migration from V1.0

### Automatic Migration

#### **If you have existing JSON files:**
```bash
# V1.0 files that will be migrated:
# - jobs_communication.json
# - jobs_design.json  
# - jobs_restauration.json

# Run migration
make db-migrate
# or
python -m france_chomage db-migrate
```

#### **Migration Process:**
1. **Backup existing data** (automatic)
2. **Create database tables**
3. **Convert JSON to database records**
4. **Validate data integrity**
5. **Mark all existing jobs as unsent** (so they can be sent again)

### Manual Migration

#### **Export from V1.0:**
```bash
# If you need to manually export V1.0 data
python -c "
import json
from pathlib import Path

# Read all V1.0 JSON files
for category in ['communication', 'design', 'restauration']:
    file_path = Path(f'jobs_{category}.json')
    if file_path.exists():
        with open(file_path) as f:
            jobs = json.load(f)
        print(f'{category}: {len(jobs)} jobs')
        
        # Export to CSV for manual review
        import pandas as pd
        df = pd.DataFrame(jobs)
        df.to_csv(f'v1_export_{category}.csv', index=False)
        print(f'Exported to v1_export_{category}.csv')
"
```

#### **Import to V2.0:**
```bash
# After setting up V2.0 database
python -c "
import json
import asyncio
from pathlib import Path
from france_chomage.database.migration_utils import migrate_json_to_database
from france_chomage.database.connection import async_session_factory, initialize_database

async def manual_import():
    initialize_database()
    async with async_session_factory() as session:
        for category in ['communication', 'design', 'restauration']:
            file_path = f'jobs_{category}.json'
            if Path(file_path).exists():
                count = await migrate_json_to_database(session, file_path, category)
                print(f'Imported {count} jobs for {category}')

asyncio.run(manual_import())
"
```

### Verification

#### **Compare V1.0 vs V2.0 data:**
```bash
# Check job counts match
python -c "
import json
from pathlib import Path

# V1.0 counts
v1_counts = {}
for category in ['communication', 'design', 'restauration']:
    file_path = Path(f'jobs_{category}.json')
    if file_path.exists():
        with open(file_path) as f:
            v1_counts[category] = len(json.load(f))

print('V1.0 Job Counts:', v1_counts)
print('Check V2.0 counts with: make db-status')
"
```

---

## 🎯 Success Criteria

### ✅ **Local Testing Success**
- [ ] Database initializes without errors
- [ ] Scraping saves jobs to database  
- [ ] Only unsent jobs are sent to Telegram
- [ ] Date format shows as dd/mm/yyyy
- [ ] No duplicate jobs sent
- [ ] Database status shows correct counts

### ✅ **Production Deployment Success**
- [ ] Railway/Docker deployment completes
- [ ] Database connects successfully
- [ ] Scheduled jobs run automatically
- [ ] Telegram messages sent correctly
- [ ] Health checks pass
- [ ] Logs show no errors

### ✅ **Database Visualization Success**
- [ ] Can connect to database via psql/Adminer
- [ ] Queries return expected data
- [ ] Statistics match application reports
- [ ] Performance is acceptable
- [ ] Backup/restore works

**🎉 Congratulations! Your France Chômage Bot V2.0 is ready for production!**
