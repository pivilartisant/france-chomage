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
TOPIC_ID = int(os.getenv('TELEGRAM_COMMUNICATION_TOPIC_ID'))  # topic ID for communication

class JobTelegramBot:
    def __init__(self, bot_token, group_id, topic_id, jobs_file='jobs_communication.json', job_type='communication'):
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
    
    def escape_markdown(self, text):
        """Échappe les caractères spéciaux Markdown"""
        if not text:
            return ""
        # Échappe les caractères problématiques pour Telegram Markdown
        escape_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    def format_job_message(self, job):
        """Format a job posting for Telegram in French"""
        # Échappe tous les textes
        title = self.escape_markdown(job.get('title', ''))
        company = self.escape_markdown(job.get('company', ''))
        location = self.escape_markdown(job.get('location', ''))
        date_posted = self.escape_markdown(job.get('date_posted', ''))
        
        message = f"🎯 *{title}*\n\n"
        message += f"🏢 *{company}*\n"
        message += f"📍 {location}\n"
        message += f"📅 Publié le : {date_posted}\n"
        
        if job.get('is_remote') == 'True':
            message += f"🏠 Télétravail possible\n"
            
        if job.get('salary_source'):
            salary = self.escape_markdown(job.get('salary_source', ''))
            message += f"💰 {salary}\n"
            
        # URL sans échappement car Telegram gère ça
        job_url = job.get('job_url', '')
        message += f"\n🔗 [Postuler ici]({job_url})\n"
        
        # Description avec échappement
        if job.get('description'):
            desc = job['description'][:200].replace('\n', ' ').strip()
            desc = self.escape_markdown(desc)
            message += f"\n📝 {desc}\\.\\.\\."
        
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
                try:
                    await self.bot.send_message(
                        chat_id=self.group_id,
                        message_thread_id=self.topic_id,
                        text=message,
                        parse_mode='MarkdownV2',
                        disable_web_page_preview=False
                    )
                except Exception as e:
                    print(f"⚠️ Erreur envoi message, tentative sans Markdown: {str(e)[:100]}")
                    # Fallback sans formatage
                    clean_message = message.replace('*', '').replace('\\', '').replace('_', '')
                    await self.bot.send_message(
                        chat_id=self.group_id,
                        message_thread_id=self.topic_id,
                        text=clean_message,
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
