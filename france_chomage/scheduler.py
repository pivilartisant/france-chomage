"""
Scheduler principal pour le bot France Chômage - Version corrigée
"""
import asyncio
import schedule
import time
from france_chomage.config import settings
from france_chomage.scraping import CommunicationScraper, DesignScraper, RestaurationScraper
from france_chomage.telegram.bot import telegram_bot
from france_chomage.database.connection import initialize_database

# Variables globales pour les statistiques
job_stats = {}

async def run_communication_jobs():
    """Scrape et envoie les offres de communication"""
    print("📢 Lancement des offres communication...")
    
    try:
        print("📡 Scraping communication en cours...")
        scraper = CommunicationScraper()
        jobs = await scraper.scrape()
        
        print(f"📦 {len(jobs)} offres scrapées")
        
        print("📤 Envoi vers Telegram...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category="communication",
            topic_id=settings.telegram_communication_topic_id
        )
        
        print(f"✅ {sent_count} nouvelles offres communication envoyées")
        
        # Sauvegarder les stats
        job_stats['communication'] = {'jobs_sent': sent_count}
        
    except Exception as e:
        print(f"❌ Erreur communication: {e}")
        job_stats['communication'] = {'jobs_sent': 0, 'error': str(e)}

async def run_design_jobs():
    """Scrape et envoie les offres de design"""
    print("🎨 Lancement des offres design...")
    
    try:
        print("📡 Scraping design en cours...")
        scraper = DesignScraper()
        jobs = await scraper.scrape()
        
        print(f"📦 {len(jobs)} offres scrapées")
        
        print("📤 Envoi vers Telegram...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category="design",
            topic_id=settings.telegram_design_topic_id
        )
        
        print(f"✅ {sent_count} nouvelles offres design envoyées")
        
        # Sauvegarder les stats
        job_stats['design'] = {'jobs_sent': sent_count}
        
    except Exception as e:
        print(f"❌ Erreur design: {e}")
        job_stats['design'] = {'jobs_sent': 0, 'error': str(e)}

async def run_restauration_jobs():
    """Scrape et envoie les offres de restauration"""
    print("🍽️ Lancement des offres restauration...")
    
    try:
        print("📡 Scraping restauration en cours...")
        scraper = RestaurationScraper()
        jobs = await scraper.scrape()
        
        print(f"📦 {len(jobs)} offres scrapées")
        
        print("📤 Envoi vers Telegram...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category="restauration",
            topic_id=settings.telegram_restauration_topic_id
        )
        
        print(f"✅ {sent_count} nouvelles offres restauration envoyées")
        
        # Sauvegarder les stats
        job_stats['restauration'] = {'jobs_sent': sent_count}
        
    except Exception as e:
        print(f"❌ Erreur restauration: {e}")
        job_stats['restauration'] = {'jobs_sent': 0, 'error': str(e)}

async def send_update_summary():
    """Envoie un résumé des statistiques vers le topic général"""
    if job_stats:
        print("📊 Envoi du résumé des mises à jour...")
        await telegram_bot.send_update_summary(job_stats)
        # Réinitialiser les stats après envoi
        job_stats.clear()

# Wrapper synchrone pour les jobs schedulés
def sync_communication_jobs():
    """Wrapper synchrone pour communication"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Reset database connection for this loop
        from france_chomage.database import connection
        connection.engine = None
        connection.async_session_factory = None
        loop.run_until_complete(run_communication_jobs())
    finally:
        loop.close()

def sync_design_jobs():
    """Wrapper synchrone pour design"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Reset database connection for this loop
        from france_chomage.database import connection
        connection.engine = None
        connection.async_session_factory = None
        loop.run_until_complete(run_design_jobs())
    finally:
        loop.close()

def sync_restauration_jobs():
    """Wrapper synchrone pour restauration"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Reset database connection for this loop
        from france_chomage.database import connection
        connection.engine = None
        connection.async_session_factory = None
        loop.run_until_complete(run_restauration_jobs())
    finally:
        loop.close()

def sync_update_summary():
    """Wrapper synchrone pour résumé"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Reset database connection for this loop
        from france_chomage.database import connection
        connection.engine = None
        connection.async_session_factory = None
        loop.run_until_complete(send_update_summary())
    finally:
        loop.close()

def main():
    """Point d'entrée principal - Synchrone"""
    # Initialize database
    initialize_database()

    # Planification des jobs
    schedule.every().day.at("17:00").do(sync_communication_jobs).tag('communication')
    schedule.every().day.at("18:00").do(sync_design_jobs).tag('design')
    schedule.every().day.at("19:00").do(sync_restauration_jobs).tag('restauration')

    # Résumé envoyé après chaque job avec délai
    schedule.every().day.at("17:05").do(sync_update_summary).tag('summary')
    schedule.every().day.at("18:05").do(sync_update_summary).tag('summary')
    schedule.every().day.at("19:05").do(sync_update_summary).tag('summary')

    print("📅 Jobs planifiés:")
    print("📢 Communication: 17:00")
    print("🎨 Design: 18:00")
    print("🍽️ Restauration: 19:00")
    print("📊 Résumés: 17:05, 18:05, 19:05")

    # Exécution immédiate en cas de démarrage (sauf si désactivé)
    if not settings.skip_init_job:
        print("\n🚀 Exécution des jobs de démarrage...")
        sync_communication_jobs()
        sync_design_jobs()
        sync_restauration_jobs()
    else:
        print("⏭️ Jobs de démarrage ignorés (SKIP_INIT_JOB=1)")

    print("\n⏰ Planification activée. Appuyez sur Ctrl+C pour arrêter.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Scheduler arrêté")

if __name__ == "__main__":
    main()
