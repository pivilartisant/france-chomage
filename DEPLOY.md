# Déploiement du Bot Telegram

## Variables d'environnement requises

Peu importe le service, vous devez définir :
- `TELEGRAM_BOT_TOKEN` : token obtenu de @BotFather
- `TELEGRAM_CHANNEL_ID` : ID de votre canal (ex: @moncanal ou -1001234567890)

## Test local avec Docker

```bash
# Build l'image
docker build -t telegram-job-bot .

# Run avec variables d'env
docker run -e TELEGRAM_BOT_TOKEN=your_token -e TELEGRAM_CHANNEL_ID=@yourchannel telegram-job-bot
```

Le bot fonctionnera 24/7 et postera automatiquement les offres à 9h et 17h.
