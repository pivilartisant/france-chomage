# 🇫🇷 France Chômage Bot

Bot Telegram automatisé pour scraper et publier les offres d'emploi en communication et design.

## 📁 Structure du projet

```
france-chomage/
├── france_chomage/           # Package principal
│   ├── config.py            # Configuration centralisée
│   ├── scheduler.py         # Scheduler principal
│   ├── cli.py               # Interface CLI
│   ├── models/job.py        # Modèle Job avec validation
│   ├── scraping/            # Scrapers (communication, design)
│   └── telegram/bot.py      # Bot Telegram
├── requirements.txt
└── .env                     # Configuration
```

## ⚡ Utilisation

```bash
# Scraping
python -m france_chomage scrape communication
python -m france_chomage scrape design

# Workflow complet (scrape + envoi)
python -m france_chomage workflow communication
python -m france_chomage workflow design

# Scheduler automatique
python -m france_chomage scheduler

# Informations
python -m france_chomage info
```

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

## 🐳 Docker

```bash
# Build image
docker build -t france-chomage-bot .

# Run with environment file
docker run --env-file .env france-chomage-bot
```
