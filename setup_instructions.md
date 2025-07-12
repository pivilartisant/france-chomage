# Telegram Job Bot Setup

## 1. Create Telegram Bot
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. Save the bot token

## 2. Create Telegram Channel
1. Create a new channel in Telegram
2. Add your bot as an administrator
3. Get the channel ID (use @userinfobot or check channel info)

## 3. Configuration
Modifiez le fichier `.env` avec vos informations :
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@yourchannel
```

## 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## 5. Run the Bot
```bash
# Run once
python telegram_bot.py

# Run with scheduler (daily at 9 AM and 5 PM)
python scheduler.py
```

## Features
- Fetches communication jobs from Indeed and LinkedIn in Paris
- Formats job postings with company, location, date
- Posts to your Telegram channel
- Includes apply links and job descriptions
- Rate limiting to avoid spam
- Scheduled posting twice daily
