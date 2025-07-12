"""
Nouveau scheduler utilisant APScheduler
"""
import asyncio
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from france_chomage.config import settings
from france_chomage.scraping import CommunicationScraper, DesignScraper
from france_chomage.telegram.bot import telegram_bot

# Configuration du logging structuré
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class JobScheduler:
    """Scheduler principal utilisant APScheduler"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.logger = logger.bind(component="scheduler")
        
    async def communication_flow(self):
        """Workflow complet communication : scrape + envoi Telegram"""
        self.logger.info("🎯 Début workflow communication")
        
        try:
            # Scraping
            scraper = CommunicationScraper()
            jobs = await scraper.scrape()
            
            if not jobs:
                self.logger.warning("Aucune offre communication trouvée")
                return
            
            # Envoi Telegram
            sent_count = await telegram_bot.send_jobs(
                jobs=jobs,
                topic_id=settings.telegram_communication_topic_id,
                job_type="communication"
            )
            
            self.logger.info("Workflow communication terminé", 
                           jobs_found=len(jobs), jobs_sent=sent_count)
            
        except Exception as exc:
            self.logger.error("Erreur workflow communication", 
                            error=str(exc), exc_info=True)
    
    async def design_flow(self):
        """Workflow complet design : scrape + envoi Telegram"""
        self.logger.info("🎨 Début workflow design")
        
        try:
            # Scraping
            scraper = DesignScraper()
            jobs = await scraper.scrape()
            
            if not jobs:
                self.logger.warning("Aucune offre design trouvée")
                return
            
            # Envoi Telegram
            sent_count = await telegram_bot.send_jobs(
                jobs=jobs,
                topic_id=settings.telegram_design_topic_id,
                job_type="design"
            )
            
            self.logger.info("Workflow design terminé",
                           jobs_found=len(jobs), jobs_sent=sent_count)
            
        except Exception as exc:
            self.logger.error("Erreur workflow design",
                            error=str(exc), exc_info=True)
    
    def setup_jobs(self):
        """Configure les tâches planifiées"""
        
        # Communication : heures configurables
        for hour in settings.communication_hours:
            self.scheduler.add_job(
                self.communication_flow,
                CronTrigger(hour=hour, minute=0),
                id=f'communication_{hour}h',
                name=f'Communication {hour}h',
                replace_existing=True
            )
            self.logger.info("Job communication programmé", hour=hour)
        
        # Design : heures configurables  
        for hour in settings.design_hours:
            self.scheduler.add_job(
                self.design_flow,
                CronTrigger(hour=hour, minute=0),
                id=f'design_{hour}h',
                name=f'Design {hour}h',
                replace_existing=True
            )
            self.logger.info("Job design programmé", hour=hour)
    
    async def run_initial_jobs(self):
        """Exécute les jobs immédiatement si configuré"""
        if settings.skip_init_job:
            self.logger.info("⏭️ Jobs initiaux ignorés (SKIP_INIT_JOB=1)")
            return
        
        self.logger.info("🚀 Exécution des jobs initiaux")
        
        # Exécute les deux workflows en parallèle
        await asyncio.gather(
            self.communication_flow(),
            self.design_flow(),
            return_exceptions=True
        )
    
    async def start(self):
        """Démarre le scheduler"""
        self.logger.info("🤖 Démarrage du scheduler")
        self.logger.info("Configuration", 
                        communication_hours=settings.communication_hours,
                        design_hours=settings.design_hours,
                        skip_init=settings.skip_init_job)
        
        # Configure les jobs
        self.setup_jobs()
        
        # Démarre le scheduler
        self.scheduler.start()
        self.logger.info("⏰ Scheduler APScheduler démarré")
        
        # Exécute les jobs initiaux si configuré
        await self.run_initial_jobs()
        
        self.logger.info("✅ Scheduler prêt - en attente des tâches programmées")
        
        try:
            # Maintient le scheduler en vie
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("🛑 Arrêt du scheduler demandé")
            self.scheduler.shutdown()
            self.logger.info("Scheduler arrêté")

# Point d'entrée principal
async def main():
    """Point d'entrée principal du scheduler"""
    scheduler = JobScheduler()
    await scheduler.start()

if __name__ == "__main__":
    asyncio.run(main())
