"""
Simple scheduler like the original v1.0
"""
import schedule
import time
import asyncio
from france_chomage.config import settings
from france_chomage.scraping import CommunicationScraper, DesignScraper, RestaurationScraper
from france_chomage.telegram.bot import telegram_bot

def run_communication_jobs():
    """Scrape et envoie les offres de communication"""
    print("🎯 Lancement des offres communication...")
    
    async def async_communication():
        try:
            print("📡 Scraping communication en cours...")
            scraper = CommunicationScraper()
            jobs = await scraper.scrape()
            
            if not jobs:
                print("⚠️ Aucune offre communication trouvée")
                return
            
            print(f"📦 {len(jobs)} offres trouvées")
            
            print("📤 Envoi vers Telegram...")
            sent_count = await telegram_bot.send_jobs(
                jobs=jobs,
                topic_id=settings.telegram_communication_topic_id,
                job_type="communication"
            )
            
            print(f"✅ {sent_count} offres communication envoyées")
            
        except Exception as e:
            print(f"❌ Erreur communication: {e}")
    
    # Run async function
    asyncio.run(async_communication())

def run_design_jobs():
    """Scrape et envoie les offres de design"""
    print("🎨 Lancement des offres design...")
    
    async def async_design():
        try:
            print("📡 Scraping design en cours...")
            scraper = DesignScraper()
            jobs = await scraper.scrape()
            
            if not jobs:
                print("⚠️ Aucune offre design trouvée")
                return
            
            print(f"📦 {len(jobs)} offres trouvées")
            
            print("📤 Envoi vers Telegram...")
            sent_count = await telegram_bot.send_jobs(
                jobs=jobs,
                topic_id=settings.telegram_design_topic_id,
                job_type="design"
            )
            
            print(f"✅ {sent_count} offres design envoyées")
            
        except Exception as e:
            print(f"❌ Erreur design: {e}")
    
    # Run async function
    asyncio.run(async_design())

def run_restauration_jobs():
    """Scrape et envoie les offres de restauration"""
    print("🍽️ Lancement des offres restauration...")
    
    async def async_restauration():
        try:
            print("📡 Scraping restauration en cours...")
            scraper = RestaurationScraper()
            jobs = await scraper.scrape()
            
            if not jobs:
                print("⚠️ Aucune offre restauration trouvée")
                return
            
            print(f"📦 {len(jobs)} offres trouvées")
            
            print("📤 Envoi vers Telegram...")
            sent_count = await telegram_bot.send_jobs(
                jobs=jobs,
                topic_id=settings.telegram_restauration_topic_id,
                job_type="restauration"
            )
            
            print(f"✅ {sent_count} offres restauration envoyées")
            
        except Exception as e:
            print(f"❌ Erreur restauration: {e}")
    
    # Run async function
    asyncio.run(async_restauration())

# Schedule jobs
for hour in settings.communication_hours:
    schedule.every().day.at(f"{hour:02d}:00").do(run_communication_jobs)
    print(f"📅 Communication programmée à {hour:02d}:00")

for hour in settings.design_hours:
    schedule.every().day.at(f"{hour:02d}:00").do(run_design_jobs)
    print(f"🎨 Design programmé à {hour:02d}:00")

for hour in settings.restauration_hours:
    schedule.every().day.at(f"{hour:02d}:00").do(run_restauration_jobs)
    print(f"🍽️ Restauration programmée à {hour:02d}:00")

print("🤖 Planificateur démarré.")

# Exécute immédiatement si configuré
if not settings.skip_init_job:
    print("🚀 Exécution immédiate des jobs au démarrage...")
    run_communication_jobs()
    run_design_jobs()
    run_restauration_jobs()
else:
    print("⏭️ Jobs de démarrage ignorés (SKIP_INIT_JOB=1)")

print("\n⏰ Planification activée. Appuyez sur Ctrl+C pour arrêter.")

def main():
    """Point d'entrée principal"""
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Scheduler arrêté")

if __name__ == "__main__":
    main()
