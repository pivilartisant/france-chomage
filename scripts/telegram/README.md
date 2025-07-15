# Telegram Scripts

This directory contains utility scripts for managing Telegram forum topics and bot operations.

⚠️ **Note:** These scripts were used for initial setup to create forum topics and update `categories.yml`. They are no longer needed for normal operation since all topic IDs are now managed through `categories.yml`.

## Files

### `create_telegram_topics.py`
Main script to create forum topics for all job categories and update `categories.yml` with the new topic IDs.

**Usage:**
```bash
python create_telegram_topics.py
```

**Requirements:**
- Bot must be an administrator in the Telegram group
- Bot must have "Manage Topics" permission
- Group must have forum topics enabled

### `resume_topic_creation.py`
Resume topic creation for categories that failed during the initial run (handles rate limiting better).

**Usage:**
```bash
python resume_topic_creation.py
```

### `get_chat_id.py`
Utility to get the numeric chat ID from a Telegram group username.

**Usage:**
```bash
python get_chat_id.py
```

### `test_bot_permissions.py`
Test script to verify bot permissions and ability to create topics.

**Usage:**
```bash
python test_bot_permissions.py
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements_telegram.txt
```

2. Ensure your `.env` file contains:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_GROUP_ID=@YourGroupUsername
```

3. Make sure your bot is an administrator in the group with "Manage Topics" permission.

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_GROUP_ID`: Your Telegram group username (e.g., @FranceChomage)

## Notes

- The scripts automatically handle rate limiting from Telegram API
- Topics are created with formatted names (e.g., "Jeu Vidéo", "Art & Culture")
- The `categories.yml` file is updated automatically with new topic IDs
- All scripts include proper error handling and logging
