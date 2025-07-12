"""
Bot Telegram générique et réutilisable
"""
import asyncio
from typing import List
import structlog

from telegram import Bot
from france_chomage.config import settings
from france_chomage.models import Job

logger = structlog.get_logger()

class TelegramJobBot:
    """Bot Telegram générique pour poster des offres d'emploi"""
    
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.group_id = settings.telegram_group_id
        self.logger = logger.bind(component="telegram_bot")
    
    def escape_markdown(self, text: str) -> str:
        """Échappe les caractères spéciaux MarkdownV2"""
        if not text:
            return ""
        
        # Caractères à échapper pour MarkdownV2
        escape_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def format_job_message(self, job: Job, job_type: str) -> str:
        """Formate un message Telegram pour une offre"""
        
        # Échappement des textes
        title = self.escape_markdown(job.display_title)
        company = self.escape_markdown(job.company)
        location = self.escape_markdown(job.location)
        date_posted = self.escape_markdown(job.date_posted)
        
        # Construction du message
        message = f"🎯 *{title}*\n\n"
        message += f"🏢 *{company}*\n"
        message += f"📍 {location}\n"
        message += f"📅 Publié le : {date_posted}\n"
        
        # Télétravail
        if job.is_remote:
            message += "🏠 Télétravail possible\n"
        
        # Salaire
        if job.salary_source:
            salary = self.escape_markdown(job.salary_source)
            message += f"💰 {salary}\n"
        
        # Lien (pas d'échappement, Telegram gère)
        message += f"\n🔗 [Postuler ici]({job.job_url})\n"
        
        # Description courte
        if job.description:
            desc = self.escape_markdown(job.short_description)
            message += f"\n📝 {desc}"
            if len(job.description) > 200:
                message += "\\.\\.\\."
        
        # Hashtags
        message += f"\n\n#{job.site} #{job_type} #Paris #emploi"
        
        return message
    
    async def send_job(self, job: Job, topic_id: int, job_type: str) -> bool:
        """Envoie une offre sur Telegram"""
        try:
            message = self.format_job_message(job, job_type)
            
            await self.bot.send_message(
                chat_id=self.group_id,
                message_thread_id=topic_id,
                text=message,
                parse_mode='MarkdownV2',
                disable_web_page_preview=False
            )
            
            self.logger.info("Offre envoyée", title=job.title, topic_id=topic_id)
            return True
            
        except Exception as exc:
            self.logger.warning(
                "Échec envoi avec Markdown, tentative sans formatage",
                title=job.title,
                error=str(exc)
            )
            
            try:
                # Fallback sans formatage
                clean_message = self.format_job_message(job, job_type)
                clean_message = clean_message.replace('*', '').replace('\\', '').replace('_', '')
                
                await self.bot.send_message(
                    chat_id=self.group_id,
                    message_thread_id=topic_id,
                    text=clean_message,
                    disable_web_page_preview=False
                )
                
                self.logger.info("Offre envoyée (sans formatage)", title=job.title)
                return True
                
            except Exception as exc2:
                self.logger.error(
                    "Échec total envoi offre",
                    title=job.title,
                    error=str(exc2),
                    exc_info=True
                )
                return False
    
    async def send_jobs(self, jobs: List[Job], topic_id: int, job_type: str) -> int:
        """Envoie une liste d'offres"""
        if not jobs:
            self.logger.warning("Aucune offre à envoyer", topic_id=topic_id)
            return 0
        
        self.logger.info("Début envoi offres", count=len(jobs), topic_id=topic_id)
        
        sent_count = 0
        for job in jobs:
            success = await self.send_job(job, topic_id, job_type)
            if success:
                sent_count += 1
            
            # Rate limiting
            await asyncio.sleep(2)
        
        self.logger.info("Envoi terminé", sent=sent_count, total=len(jobs))
        return sent_count

# Instance globale
telegram_bot = TelegramJobBot()
