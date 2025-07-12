# Test Local du Bot

## 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

## 2. Configuration

Modifiez le fichier `.env` avec vos vraies informations :
```
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF...
TELEGRAM_CHANNEL_ID=@votre_canal
```

## 3. Tests

### Test simple (une fois)
```bash
python telegram_bot.py
```

### Test avec planificateur
```bash
python scheduler.py
```

### Test avec Docker
```bash
# Build l'image
docker build -t job-bot .

# Run le container
docker run --env-file .env job-bot
```

## 4. Vérifications

- [ ] Le bot se connecte sans erreur
- [ ] Les offres sont récupérées depuis Indeed/LinkedIn  
- [ ] Les messages apparaissent dans votre canal Telegram
- [ ] Le format des messages est correct en français

## 5. Debug

Si ça ne marche pas :
- Vérifiez que le bot est administrateur du canal
- Testez le token avec `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Vérifiez l'ID du canal avec @userinfobot
