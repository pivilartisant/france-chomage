# France Chomage Bot

Automated Telegram bot to scrape and publish job offers across different categories with separated scraping/sending architecture.

## Project Overview
Use [Jobspy](https://github.com/speedyapply/JobSpy) <3 


### Database Setup (First Time)
```bash
# Initialize database tables (safe, preserves existing data)
make db-init

# Migrate existing JSON data (if any)
make db-migrate

# Create backup before changes
make db-backup
```

## Configuration (.env)

```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_GROUP_ID=your_group_id
DATABASE_URL=your_database_url
SKIP_INIT_JOB=1 # Skip initial job setup (set to 0 to run init job)
DOCKER_ENV=true # true if running in Docker
FORCE_DOCKER_MODE=0  
RESULTS_WANTED=10   # Number of job offers to scrape per category               
SCRAPE_DELAY_MIN=2.0 # Minimum delay between scrapes (in seconds)
SCRAPE_DELAY_MAX=5.0 # Maximum delay between scrapes (in seconds)
```

**Note:** All categories with their topic IDs and schedules are managed through `categories.yml` file.

## Scheduling System

The bot uses a **separated architecture** with independent scraping and sending operations:

- **Scraping**: Distributed across 24 hours (max 3 categories per hour)
- **Sending**: Runs 1 hour after scraping for each category
- **Even distribution**: No clustering, optimal resource usage
- **Independent operations**: Scraping failures don't block sending

### Example Schedule:
```
00:00 - Scrape: aeronautique, immobilier, vente
01:00 - Send: aeronautique, immobilier, vente | Scrape: agent_assurance, industrie  
02:00 - Send: agent_assurance, industrie | Scrape: agriculture, ingénieur_electronique
...
```

View complete schedule: `python -m france_chomage utils info`

## Available Categories

See: `categories.yml`

## Documentation

- **[Complete Documentation](docs/)** - All guides and references
- **[Development Guide](docs/DEV.md)** - Setup for developers
- **[Database Setup](docs/DATABASE_SETUP.md)** - Database configuration
- **[Safe Deployment Guide](docs/ADD_CATEGORIES.md)** - How to add new job categories safely

## Development

For development instructions and adding new job categories, see **[Development Guide](docs/AGENT.md)**.

## License

Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
