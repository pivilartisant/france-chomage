# 🇫🇷 France Chômage Bot

Bot Telegram automatisé pour scraper et publier les offres d'emploi en communication, design et restauration.

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

### 📡 Commandes de Scraping
```bash
# Scraping seulement (sauvegarde dans jobs_*.json)
python -m france_chomage scrape communication
python -m france_chomage scrape design
python -m france_chomage scrape restauration
```

### 📤 Commandes d'Envoi
```bash
# Envoi seulement (lit depuis jobs_*.json)
python -m france_chomage send communication
python -m france_chomage send design  
python -m france_chomage send restauration
```

### 🔄 Workflow Complet
```bash
# Scrape + Envoi automatique
python -m france_chomage workflow communication
python -m france_chomage workflow design
python -m france_chomage workflow restauration
```

### 🤖 Automatisation
```bash
# Scheduler automatique (lance les workflows selon planning)
python -m france_chomage scheduler

# Informations de configuration
python -m france_chomage info
```

### 💡 Exemples d'Usage

**Utilisation séparée :**
```bash
# 1. Scraper uniquement (pour tester/debug)
python -m france_chomage scrape design
# Génère: jobs_design.json

# 2. Envoyer plus tard (par exemple après vérification manuelle)
python -m france_chomage send design
```

**Workflow automatique :**
```bash
# Tout en une commande
python -m france_chomage workflow restauration
```

**Planning automatisé :**
- Communication: 17:00
- Design: 18:00  
- Restauration: 19:00

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

## 🐳 Docker

```bash
# Build image
docker build -t france-chomage-bot .

# Run with environment file
docker run --env-file .env france-chomage-bot
```

## 🔧 Ajouter une Nouvelle Catégorie

Pour ajouter une nouvelle catégorie (ex: "marketing"), suivez ces étapes:

### 1. Créer le Scraper
```bash
# Créer france_chomage/scraping/marketing.py
```
```python
from .base import ScraperBase

class MarketingScraper(ScraperBase):
    search_terms = "marketing OR growth OR acquisition"
    filename_prefix = "marketing"
    job_type = "marketing"
```

### 2. Mettre à Jour les Imports
```python
# Dans france_chomage/scraping/__init__.py
from .marketing import MarketingScraper
__all__ = [..., "MarketingScraper"]
```

### 3. Ajouter la Configuration
```python
# Dans france_chomage/config.py
self.telegram_marketing_topic_id = int(os.getenv("TELEGRAM_MARKETING_TOPIC_ID", "60"))
self.marketing_hours = [20]
```

### 4. Mettre à Jour le CLI
```python
# Dans france_chomage/cli.py - ajouter dans chaque command:
elif domain == "marketing":
    scraper = MarketingScraper()
    topic_id = settings.telegram_marketing_topic_id
```

### 5. Mettre à Jour le Scheduler
```python
# Dans france_chomage/scheduler.py
def run_marketing_jobs():
    # Copier la structure de run_design_jobs()
    
# Ajouter la programmation:
for hour in settings.marketing_hours:
    schedule.every().day.at(f"{hour:02d}:00").do(run_marketing_jobs)
```

### 6. Variables d'Environnement
```env
# Ajouter dans .env
TELEGRAM_MARKETING_TOPIC_ID=60
```

### 7. Test
```bash
python -m france_chomage scrape marketing
python -m france_chomage workflow marketing
```
