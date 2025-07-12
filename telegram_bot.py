import asyncio
import json
from telegram import Bot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')  # e.g., '-1001234567890'
TOPIC_ID = int(os.getenv('TELEGRAM_TOPIC_ID', '3'))  # topic ID for communication

class JobTelegramBot:
    def __init__(self, bot_token, group_id, topic_id, jobs_file='jobs.json', job_type='communication'):
        self.bot = Bot(token=bot_token)
        self.group_id = group_id
        self.topic_id = topic_id
        self.jobs_file = jobs_file
        self.job_type = job_type
        
    def load_existing_jobs(self):
        """Load jobs from existing jobs file"""
        try:
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            return jobs
        except FileNotFoundError:
            print(f"Fichier {self.jobs_file} introuvable. Lancez d'abord le script correspondant")
            return []
    
    def format_job_message(self, job):
        """Format a job posting for Telegram in French"""
        message = f"🎯 **{job['title']}**\n\n"
        message += f"🏢 **{job['company']}**\n"
        message += f"📍 {job['location']}\n"
        message += f"📅 Publié le : {job['date_posted']}\n"
        
        if job.get('is_remote') == 'True':
            message += f"🏠 Télétravail possible\n"
            
        if job.get('salary_source'):
            message += f"💰 {job['salary_source']}\n"
            
        message += f"\n🔗 [Postuler ici]({job['job_url']})\n"
        
        # Add description preview (first 200 chars)
        if job.get('description'):
            desc = job['description'][:200].replace('\n', ' ').strip()
            message += f"\n📝 {desc}..."
            
        message += f"\n\n#{job['site']} #{self.job_type} #Paris #emploi"
        
        return message
    
    async def send_jobs_to_topic(self):
        """Send jobs to Telegram group topic"""
        try:
            print(f"Chargement des offres d'emploi {self.job_type}...")
            jobs = self.load_existing_jobs()
            print(f"Trouvé {len(jobs)} offres de {self.job_type}")
            
            if not jobs:
                print(f"Aucune offre {self.job_type} trouvée. Lancez le script correspondant d'abord.")
                return
            
            for job in jobs:
                message = self.format_job_message(job)
                await self.bot.send_message(
                    chat_id=self.group_id,
                    message_thread_id=self.topic_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                print(f"Offre envoyée : {job['title']}")
                await asyncio.sleep(2)  # Rate limiting
                
        except Exception as e:
            print(f"Erreur : {e}")
            
    async def run(self):
        """Run the bot"""
        await self.send_jobs_to_topic()

async def main():
    if not BOT_TOKEN or not GROUP_ID:
        print("Veuillez définir TELEGRAM_BOT_TOKEN et TELEGRAM_GROUP_ID dans le fichier .env")
        return
        
    bot = JobTelegramBot(BOT_TOKEN, GROUP_ID, TOPIC_ID)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
