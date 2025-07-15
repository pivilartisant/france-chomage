"""
Bot Telegram générique et réutilisable
"""
import asyncio
from typing import List

from telegram import Bot
from telegram.request import HTTPXRequest
from france_chomage.config import settings
from france_chomage.database import job_manager
from france_chomage.database.models import Job as DBJob

class TelegramJobBot:
    """Bot Telegram générique pour poster des offres d'emploi"""
    
    def __init__(self):
        # Configuration HTTPXRequest avec un pool de connexions plus grand
        request = HTTPXRequest(
            connection_pool_size=10,  # Augmente le pool de connexions
            pool_timeout=10.0,        # Augmente le timeout du pool
            read_timeout=10.0,        # Augmente le timeout de lecture
            write_timeout=10.0        # Augmente le timeout d'écriture
        )
        self.bot = Bot(token=settings.telegram_bot_token, request=request)
        self.group_id = settings.telegram_group_id
    
    def escape_markdown(self, text: str) -> str:
        """Échappe les caractères spéciaux MarkdownV2"""
        if not text:
            return ""
        
        # Caractères à échapper pour MarkdownV2
        escape_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def format_job_message(self, job, job_type: str) -> str:
        """Formate un message Telegram pour une offre (Job ou DBJob)"""
        
        # Échappement des textes
        title = self.escape_markdown(job.display_title)
        company = self.escape_markdown(job.company)
        location = self.escape_markdown(job.location)
        
        # Format date properly - dd/mm/yyyy
        if isinstance(job, DBJob):
            date_posted = self.escape_markdown(job.formatted_date)  # Uses dd/mm/yyyy format
        else:
            # Fallback for old Job model
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
        
        return message
    
    async def send_jobs_from_database(self, category: str, topic_id: int) -> int:
        """Send unsent jobs from database to Telegram"""
        try:
            # Get unsent jobs from database (last 30 days only)
            unsent_jobs = await job_manager.get_unsent_jobs(category, max_age_days=30)
            
            if not unsent_jobs:
                print(f"📭 Aucune nouvelle offre {category} à envoyer")
                return 0
            
            print(f"📤 Envoi de {len(unsent_jobs)} nouvelles offres {category}")
            
            sent_count = 0
            sent_job_ids = []
            
            for i, job in enumerate(unsent_jobs, 1):
                print(f"📨 Envoi {i}/{len(unsent_jobs)}: {job.title[:50]}...")
                success = await self.send_job(job, topic_id, category)
                if success:
                    sent_count += 1
                    sent_job_ids.append(job.id)
                
                # Rate limiting
                await asyncio.sleep(2)
            
            # Mark jobs as sent in database
            if sent_job_ids:
                marked_count = await job_manager.mark_jobs_as_sent(sent_job_ids)
                print(f"✅ {marked_count} jobs marqués comme envoyés en base")
            
            print(f"🎯 Envoi terminé: {sent_count}/{len(unsent_jobs)} offres envoyées")
            return sent_count
            
        except Exception as exc:
            print(f"❌ Erreur envoi jobs depuis database: {exc}")
            return 0
    
    async def send_job(self, job, topic_id: int, job_type: str) -> bool:
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
            
            print(f"✅ Offre envoyée: {job.title}")
            return True
            
        except Exception as exc:
            print(f"⚠️ Échec Markdown, essai sans formatage: {job.title}")
            
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
                
                print(f"✅ Offre envoyée (texte brut): {job.title}")
                return True
                
            except Exception as exc2:
                print(f"❌ Échec total envoi: {job.title} - {str(exc2)}")
                return False
    
    # Old send_jobs method removed - now using send_jobs_from_database
    
    async def send_update_summary(self, updates: dict) -> bool:
        """Envoie un résumé des mises à jour vers le topic général"""
        try:
            from datetime import datetime
            
            # Construction du message de résumé
            message = "📊 *Mise à jour France Chômage Bot*\n\n"
            
            # Informations par catégorie
            total_jobs = 0
            for category, info in updates.items():
                jobs_count = info.get('jobs_sent', 0)
                total_jobs += jobs_count
                emoji = {'communication': '🎯', 'design': '🎨', 'restauration': '🍽️'}.get(category, '📋')
                
                message += f"{emoji} *{category.title()}*: {jobs_count} offres\n"
                
                if info.get('error'):
                    message += f"  ⚠️ Erreur: {info['error']}\n"
            
            # Résumé total
            message += f"\n📈 *Total*: {total_jobs} nouvelles offres\n"
            message += f"🕒 *Dernière mise à jour*: {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n"
            message += "A bientôt pour plus d'offres"
            
            await self.bot.send_message(
                chat_id=self.group_id,
                message_thread_id=settings.telegram_group_id,
                text=message,
                parse_mode='MarkdownV2',
                disable_web_page_preview=True
            )
            
            print(f"📊 Résumé envoyé vers topic général ({settings.telegram_group_id})")
            return True
            
        except Exception as exc:
            print(f"❌ Erreur envoi résumé: {exc}")
            # Fallback sans formatage
            try:
                clean_message = message.replace('*', '').replace('\\', '').replace('_', '')
                await self.bot.send_message(
                    chat_id=self.group_id,
                    message_thread_id=settings.telegram_group_id,
                    text=clean_message,
                    disable_web_page_preview=True
                )
                print("📊 Résumé envoyé (texte brut)")
                return True
            except Exception as exc2:
                print(f"❌ Échec total envoi résumé: {exc2}")
                return False

# Instance globale
telegram_bot = TelegramJobBot()
