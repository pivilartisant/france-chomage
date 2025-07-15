# France Chômage Bot - Agent Guide

## Project Overview
A French Telegram bot that scrapes job offers for communication, design, and restaurant jobs, then automatically posts them to specific Telegram topics. Now features PostgreSQL database storage with automatic duplicate detection and 30-day job filtering.

## Tech Stack
- **Python 3.x** with modern typing
- **python-telegram-bot** (20.7) - Telegram bot framework
- **python-jobspy** (1.1.15) - Job scraping library
- **pandas** - Data manipulation
- **pydantic** (2.5.0) - Data validation
- **schedule** (1.2.0) - Job scheduling
- **typer** (0.9.0) - CLI framework
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

### Application Usage
```bash
# Scraping only (saves to database)
python -m france_chomage scrape communication
python -m france_chomage scrape design
python -m france_chomage scrape restauration

# Send only (reads from database, new jobs only)
python -m france_chomage send communication
python -m france_chomage send design
python -m france_chomage send restauration

# Complete workflow (scrape + send)
python -m france_chomage workflow communication
python -m france_chomage workflow design
python -m france_chomage workflow restauration

# Run scheduler (automated workflows)
python -m france_chomage scheduler
make run-scheduler

# Configuration info
python -m france_chomage info
make info

# Test configuration
python -m france_chomage test
make test-config
```

### Database Management
```bash
# Initialize database tables
make db-init
python -m france_chomage db-init

# Migrate JSON files to database
make db-migrate
python -m france_chomage db-migrate

# Show database status
make db-status
python -m france_chomage db-status

# Clean up old jobs (90+ days)
make db-cleanup
python -m france_chomage db-cleanup
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

## Project Structure
```
france_chomage/
├── config.py            # Centralized configuration
├── scheduler.py         # Main scheduler
├── cli.py               # CLI interface
├── models/job.py        # Job model with validation
├── database/            # Database models & repositories
├── scraping/            # Scrapers (communication, design, restauration)
├── telegram/bot.py      # Telegram bot
└── tests/               # Test files
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
TELEGRAM_COMMUNICATION_TOPIC_ID=3
TELEGRAM_DESIGN_TOPIC_ID=40
TELEGRAM_RESTAURATION_TOPIC_ID=326

# Optional
RESULTS_WANTED=20
LOCATION=Paris
SKIP_INIT_JOB=0
```

## Adding New Job Categories
1. Create scraper in `france_chomage/scraping/new_category.py`
2. Update imports in `france_chomage/scraping/__init__.py`
3. Add configuration in `france_chomage/config.py`
4. Update CLI in `france_chomage/cli.py`
5. Update scheduler in `france_chomage/scheduler.py`
6. Add environment variables to `.env`
7. Test with `python -m france_chomage scrape new_category`

## Scheduled Jobs
- Communication: 17:00
- Design: 18:00
- Restauration: 19:00
- Automatic summary after each workflow

## Testing
- Use `pytest` for all tests
- Tests located in `france_chomage/tests/`
- Use `pytest-asyncio` for async tests
- Use `pytest-mock` for mocking
- Coverage reports available with `make test-cov`
