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
python -m france_chomage scrape run design
python -m france_chomage scrape run restauration

# Send only (reads from database, new jobs only)
python -m france_chomage send run communication
python -m france_chomage send run design
python -m france_chomage send run restauration

# Complete workflow (scrape + send)
python -m france_chomage workflow run communication
python -m france_chomage workflow run design
python -m france_chomage workflow run restauration

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
# Initialize database tables
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
├── cli.py               # CLI interface (legacy)
├── cli/                 # Modular CLI structure
│   ├── __init__.py      # Main CLI app with sub-applications
│   ├── shared.py        # Domain validation and utilities
│   ├── scraping.py      # Scraping commands
│   ├── sending.py       # Telegram sending commands
│   ├── workflow.py      # Complete workflow commands
│   ├── database.py      # Database management commands
│   └── utils.py         # Utility commands (info, test, etc.)
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
4. Update CLI in `france_chomage/cli/shared.py` (add to VALID_DOMAINS and mappings)
5. Update scheduler in `france_chomage/scheduler.py`
6. Add environment variables to `.env`
7. Test with `python -m france_chomage scrape run new_category`

**Note**: With the new modular CLI structure, adding a new category now requires changes in only ONE place (`shared.py`) instead of multiple files!

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
