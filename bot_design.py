import asyncio
from telegram_bot import JobTelegramBot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
DESIGN_TOPIC_ID =  int(os.getenv('TELEGRAM_DESIGN_TOPIC_ID'))

async def send_design_jobs():
    """Send design jobs to topic"""
    if not BOT_TOKEN or not GROUP_ID:
        print("Variables d'environnement manquantes")
        return
        
    bot = JobTelegramBot(
        BOT_TOKEN, 
        GROUP_ID, 
        DESIGN_TOPIC_ID,
        jobs_file='jobs_design.json',
        job_type='design'
    )
    await bot.run()

if __name__ == "__main__":
    asyncio.run(send_design_jobs())
