# 🇫🇷 France Chômage Bot

Bot Telegram automatisé pour scraper et publier les offres d'emploi dans **49 catégories** avec architecture séparée scraping/envoi.

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
│   ├── scraping/            # Job scrapers (49 categories)
│   ├── telegram/            # Telegram bot
│   ├── scheduler.py         # Separated scraping/sending scheduler
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
# Initialize database tables (safe, preserves existing data)
make db-init

# Migrate existing JSON data (if any)
make db-migrate

# Create backup before changes
make db-backup
```

### 🔄 Database Migration Management
```bash
# Check migration status
python -m france_chomage migrate check

# Apply pending migrations
python -m france_chomage migrate upgrade

# Create new migration
python -m france_chomage migrate revision -m "Description"
```

### 📡 Job Scraping (Independent Operation)
```bash
# Scrape jobs only (saves to database + filters duplicates)
python -m france_chomage workflow scrape communication
python -m france_chomage workflow scrape design
python -m france_chomage workflow scrape restauration
# ... or any of the 49 categories
```

### 📤 Send to Telegram (Independent Operation)
```bash
# Send only NEW jobs from database (dd/mm/yyyy format)
python -m france_chomage workflow send communication
python -m france_chomage workflow send design
python -m france_chomage workflow send restauration
# ... or any of the 49 categories
```

### 🔄 Complete Workflow (Separated Operations)
```bash
# Scrape + Send new jobs (now separated internally)
python -m france_chomage workflow run communication
python -m france_chomage workflow run design
python -m france_chomage workflow run restauration
# ... or any of the 49 categories
```

### 🤖 Automated Scheduling (Separated Operations)
```bash
# Run scheduler (automated scraping and sending)
python -m france_chomage scheduler

# Database status
make db-status

# Configuration info (shows separate schedules)
python -m france_chomage utils info
```

## ✨ Key Features

### 🎯 **Smart Job Processing**
- **49 job categories**: Complete coverage of French job market
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
- **Safe deployments**: No data loss on updates
- **Migration management**: Alembic-powered schema evolution
- **Backup ready**: Easy export/import capabilities

### 🤖 **Separated Architecture**
- **Independent scraping**: Runs separately from sending
- **Flexible scheduling**: Different hours for scrape vs send
- **Better reliability**: Scraping failures don't block sending
- **Even distribution**: Max 3 categories per hour (no clustering)
- **Auto-summary**: Status updates after each run

## ⚙️ Configuration (.env)

```env
# Telegram (requis)
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_GROUP_ID=your_group_id

# Scraping (optionnel)
RESULTS_WANTED=20
LOCATION=Paris
SKIP_INIT_JOB=0
```

**Note:** All 49 categories with their topic IDs and schedules are managed through `categories.yml` file. No need to set individual `TELEGRAM_*_TOPIC_ID` environment variables.

## ⏰ Scheduling System

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

## 📋 Available Categories

The bot supports **49 job categories** across all sectors:

**Tech & IT**: communication, design, technologie, cybersécurité, jeu_video, ingénieur_electronique  
**Health**: sante, kinésithérapeute, aide_a_domicile, services_personne  
**Business**: finance, comptable, ressources_humaines, service_client, immobilier  
**Industry**: construction, industrie, automobile, logistique, mines_carrieres  
**Services**: restauration, tourisme, evenementiel, juridique, formation_pro  
**Creative**: art_culture, audiovisuel, mode, patrimoine_culture  
**Energy**: energie_renouvelable, energies, environnement  
**Agriculture**: agriculture, animaux  
**Transport**: transport_public, aeronautique, nautisme  
**Others**: education, sport, securite, emploi_accompagnement, assistanat, cosmetique, travaux_manuels, services_publics, vente

## 📚 Documentation

- **[📖 Complete Documentation](docs/)** - All guides and references
- **[🚀 Deployment Guide](docs/DEPLOYMENT_README.md)** - Choose your deployment method
- **[👨‍💻 Development Guide](docs/AGENT.md)** - Setup for developers
- **[🗄️ Database Setup](docs/DATABASE_SETUP.md)** - Database configuration
- **[🔐 Safe Deployment Guide](deployment/SAFE_DEPLOYMENT_GUIDE.md)** - Data-safe deployment practices
- **[📊 Workflow Report](WORKFLOW_REPORT.md)** - Detailed architecture and workflow analysis

## 🔧 Development

For development instructions and adding new job categories, see **[Development Guide](docs/AGENT.md)**.
