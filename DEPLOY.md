# Déploiement du Bot Telegram

## Railway (Recommandé)

1. Créez un compte sur [Railway](https://railway.app/)
2. Connectez votre repository GitHub
3. Sélectionnez votre projet `france-chomage`
4. Ajoutez les variables d'environnement :
   - `TELEGRAM_BOT_TOKEN` : votre token de bot
   - `TELEGRAM_CHANNEL_ID` : ID de votre canal
5. Railway déploiera automatiquement avec le `Dockerfile`

## Heroku

1. Créez une app Heroku
2. Connectez votre repository
3. Ajoutez les variables d'environnement dans Settings → Config Vars
4. Le `Procfile` sera utilisé automatiquement

## Render

1. Créez un compte sur [Render](https://render.com/)
2. Créez un nouveau "Web Service"
3. Connectez votre repository
4. Sélectionnez "Docker" comme environnement
5. Ajoutez les variables d'environnement

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
