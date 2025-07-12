# Déploiement du Bot Telegram v2.0

## Variables d'environnement requises

Variables obligatoires pour tous les services :
- `TELEGRAM_BOT_TOKEN` : token obtenu de @BotFather
- `TELEGRAM_GROUP_ID` : ID de votre groupe Telegram
- `TELEGRAM_COMMUNICATION_TOPIC_ID` : ID du topic pour les offres communication (ex: 3)
- `TELEGRAM_DESIGN_TOPIC_ID` : ID du topic pour les offres design (ex: 40)

Variables optionnelles :
- `RESULTS_WANTED=15` : nombre d'offres à récupérer par source
- `SKIP_INIT_JOB=0` : skip les jobs initiaux (0=exécuter, 1=skip)

## Example complet .env

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF...
TELEGRAM_GROUP_ID=-1001234567890
TELEGRAM_COMMUNICATION_TOPIC_ID=3
TELEGRAM_DESIGN_TOPIC_ID=40
RESULTS_WANTED=15
SKIP_INIT_JOB=0
```

## Test local avec Docker

```bash
# Build l'image
docker build -t france-chomage-bot .

# Run avec variables d'env
docker run --env-file .env france-chomage-bot
```

Le bot fonctionnera 24/7 avec :
- Offres communication → topic 3 (9h et 17h)
- Offres design → topic 40 (10h et 18h)
