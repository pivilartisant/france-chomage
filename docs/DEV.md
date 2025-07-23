# France Chômage Bot - Dev Guide

## Project Overview
A French Telegram bot that scrapes job offers different categories, then automatically posts them to specific Telegram forum topics. Features PostgreSQL database storage with automatic duplicate detection, 30-day job filtering, and separated scraping/sending architecture.

## Tech Stack
- **Python 3.x** with modern typing
- **python-telegram-bot** (20.7) - Telegram bot framework
- **python-jobspy** (1.1.15) - Job scraping library
- **pandas** - Data manipulation
- **pydantic** (2.5.0) - Data validation
- **schedule** (1.2.0) - Job scheduling
- **typer** (0.16.0) - CLI framework with rich output
- **pytest** (7.4.3) - Testing framework
- **SQLAlchemy** (2.0.23) - Database ORM
- **asyncpg** (0.29.0) - PostgreSQL async driver
- **alembic** (1.13.1) - Database migrations

## Key Commands

### Development
```bash
# Install dependencies
make install
# or
pip install -r requirements.txt

# Run tests
make test
pytest

# Run tests with coverage
make test-cov
pytest --cov=france_chomage --cov-report=html --cov-report=term

# Lint code
make lint
flake8 france_chomage/ --max-line-length=100 --ignore=E203,W503

# Format code
make format
black france_chomage/ --line-length=100

# Clean temporary files
make clean
```

### Application Usage (New Modular CLI)
```bash
# Scraping only (saves to database)
python -m france_chomage scrape run communication

# Send only (reads from database, new jobs only)
python -m france_chomage send run communication

# Complete workflow (scrape + send)
python -m france_chomage workflow run communication

# Run scheduler (automated workflows)
python -m france_chomage scheduler
make run-scheduler

# Configuration and utilities
python -m france_chomage utils info
python -m france_chomage utils test
python -m france_chomage utils update

# Get help for any command
python -m france_chomage --help
python -m france_chomage scrape --help
python -m france_chomage db --help
```

### Database Management
```bash
# Initialize database tables (safe, preserves existing data)
make db-init
python -m france_chomage db init

# Migrate JSON files to database
make db-migrate
python -m france_chomage db migrate

# Show database status
make db-status
python -m france_chomage db status

# Clean up old jobs (90+ days)
make db-cleanup
python -m france_chomage db cleanup --days 90

# Backup database to JSON files
make db-backup
python -m france_chomage db backup
```

### Migration Management
```bash
# Check migration status
make migrate-check
python -m france_chomage migrate check

# Apply pending migrations
make migrate-upgrade
python -m france_chomage migrate upgrade

# Create new migration
make migrate-create
python -m france_chomage migrate revision -m "Description"

# Show migration history
make migrate-history
python -m france_chomage migrate history
```

### Docker
```bash
# Build image
make docker-build
docker build -t france-chomage-bot .

# Run container
make docker-run
docker run --env-file .env france-chomage-bot
```

## Code Style & Conventions
- **Line length**: 100 characters (black formatting)
- **Type hints**: Use modern Python typing throughout
- **Data validation**: Use Pydantic models for data structures
- **Error handling**: Comprehensive error handling with logging
- **CLI**: Use Typer for command-line interfaces
- **Testing**: Use pytest with async support

## Environment Variables (.env)
```env
# Required
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_GROUP_ID=your_group_id

# Optional
RESULTS_WANTED=20
LOCATION=Paris
SKIP_INIT_JOB=0
```

## Adding New Job Categories

**NEW SIMPLIFIED PROCESS** (2 minutes instead of 45 minutes):

1. Edit `categories.yml` and add your category:
   ```yaml
   your_category:
     search_terms: "your search terms"
     telegram_topic_id: 600  # unique ID
     schedule_hour: 20
     enabled: true
   ```
2. Test: `python -m france_chomage scrape run your_category`

That's it! The system automatically handles scheduling, CLI integration, and validation.

See [ADDING_CATEGORIES.md](ADDING_CATEGORIES.md) for detailed documentation.

