import asyncio
from telegram_bot import JobTelegramBot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
COMMUNICATION_TOPIC_ID = int(os.getenv('TELEGRAM_TOPIC_ID', '3'))

async def send_communication_jobs():
    """Send communication jobs to topic"""
    if not BOT_TOKEN or not GROUP_ID:
        print("Variables d'environnement manquantes")
        return
        
    bot = JobTelegramBot(
        BOT_TOKEN, 
        GROUP_ID, 
        COMMUNICATION_TOPIC_ID,
        jobs_file='jobs.json',
        job_type='communication'
    )
    await bot.run()

if __name__ == "__main__":
    asyncio.run(send_communication_jobs())
