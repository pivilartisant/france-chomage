# 🇫🇷 France Chômage Bot

Bot Telegram automatisé pour scraper et publier les offres d'emploi en communication, design et restauration.

## 🚀 Quick Deploy

### Railway (Recommended - 1 Click)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

### Docker Compose (Local/VPS)
```bash
make docker-up
```

## 📁 Project Structure

```
france-chomage/
├── france_chomage/           # Main application package
│   ├── database/            # PostgreSQL models & repositories  
│   ├── scraping/            # Job scrapers (communication, design, restauration)
│   ├── telegram/            # Telegram bot
│   └── models/              # Data models
├── deployment/              # Deployment configurations
│   ├── docker/             # Docker Compose setup
│   └── railway/            # Railway cloud deployment
├── docs/                   # Documentation
├── alembic/               # Database migrations
└── requirements.txt       # Python dependencies
```

## ⚡ Usage

### 🗄️ Database Setup (First Time)
```bash
# Initialize database tables
make db-init

# Migrate existing JSON data (if any)
make db-migrate
```

### 📡 Job Scraping
```bash
# Scrape jobs (saves to database + filters duplicates)
python -m france_chomage scrape communication
python -m france_chomage scrape design
python -m france_chomage scrape restauration
```

### 📤 Send to Telegram
```bash
# Send only NEW jobs from database (dd/mm/yyyy format)
python -m france_chomage send communication
python -m france_chomage send design
python -m france_chomage send restauration
```

### 🔄 Complete Workflow
```bash
# Scrape + Send new jobs only
python -m france_chomage workflow communication
python -m france_chomage workflow design
python -m france_chomage workflow restauration
```

### 🤖 Automated Scheduling
```bash
# Run scheduler (automated workflows)
python -m france_chomage scheduler

# Database status
make db-status

# Configuration info
python -m france_chomage info
```

## ✨ Key Features

### 🎯 **Smart Job Processing**
- **30-day filtering**: Only recent, relevant jobs
- **Duplicate removal**: No more repeated job postings  
- **Auto-deduplication**: Across different job sites
- **Incremental updates**: Only new jobs are sent

### 📅 **Improved User Experience**
- **French date format**: dd/mm/yyyy in Telegram messages
- **Clean formatting**: Better readability
- **Fresh content**: Only jobs posted in last 30 days
- **No spam**: Duplicate jobs automatically filtered

### 🗄️ **Database-Powered**
- **PostgreSQL storage**: Reliable, scalable data management
- **Fast queries**: Indexed for performance
- **Data integrity**: Proper validation and constraints
- **Backup ready**: Easy export/import capabilities

### 🤖 **Automated Scheduling**
- **Communication**: 17:00 daily
- **Design**: 18:00 daily  
- **Restaurant**: 19:00 daily
- **Auto-summary**: Status updates after each run

## ⚙️ Configuration (.env)

```env
# Telegram (requis)
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_GROUP_ID=your_group_id
TELEGRAM_COMMUNICATION_TOPIC_ID=3
TELEGRAM_DESIGN_TOPIC_ID=40
TELEGRAM_RESTAURATION_TOPIC_ID=326

# Scraping (optionnel)
RESULTS_WANTED=20
LOCATION=Paris
SKIP_INIT_JOB=0
```

## 📚 Documentation

- **[📖 Complete Documentation](docs/)** - All guides and references
- **[🚀 Deployment Guide](docs/DEPLOYMENT_README.md)** - Choose your deployment method
- **[👨‍💻 Development Guide](docs/AGENT.md)** - Setup for developers
- **[🗄️ Database Setup](docs/DATABASE_SETUP.md)** - Database configuration

## 🔧 Development

For development instructions and adding new job categories, see **[Development Guide](docs/AGENT.md)**.
