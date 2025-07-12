"""
Interface en ligne de commande unifiée
"""
import asyncio
import typer

from france_chomage.config import settings
from france_chomage.scraping import CommunicationScraper, DesignScraper
from france_chomage.telegram.bot import telegram_bot
from france_chomage.environments import detect_environment

app = typer.Typer(help="🇫🇷 France Chômage Bot - CLI unifié")

@app.command()
def scrape(
    domain: str = typer.Argument(..., help="Domaine à scraper (communication/design)")
):
    """Scrape les offres d'emploi pour un domaine"""
    
    async def _scrape():
        if domain == "communication":
            scraper = CommunicationScraper()
        elif domain == "design":
            scraper = DesignScraper()
        else:
            typer.echo(f"❌ Domaine inconnu: {domain}")
            typer.echo("Domaines disponibles: communication, design")
            raise typer.Exit(1)
        
        print(f"🔍 Début scraping {domain}")
        jobs = await scraper.scrape()
        
        typer.echo(f"✅ {len(jobs)} offres trouvées pour {domain}")
        
        return jobs
    
    asyncio.run(_scrape())

@app.command()
def send(
    domain: str = typer.Argument(..., help="Domaine à envoyer (communication/design)"),
):
    """Envoie les offres sur Telegram"""
    
    async def _send():
        if domain == "communication":
            scraper = CommunicationScraper()
            topic_id = settings.telegram_communication_topic_id
        elif domain == "design":
            scraper = DesignScraper()
            topic_id = settings.telegram_design_topic_id
        else:
            typer.echo(f"❌ Domaine inconnu: {domain}")
            raise typer.Exit(1)
        
        # Charge les jobs depuis le fichier
        jobs = scraper.load_jobs()
        
        if not jobs:
            typer.echo(f"❌ Aucune offre trouvée pour {domain}")
            typer.echo(f"Lancez d'abord: python -m france_chomage scrape {domain}")
            raise typer.Exit(1)
        
        print(f"📤 Envoi de {len(jobs)} offres {domain} vers Telegram")
        
        sent_count = await telegram_bot.send_jobs(
            jobs=jobs,
            topic_id=topic_id,
            job_type=domain
        )
        
        typer.echo(f"✅ {sent_count}/{len(jobs)} offres envoyées")
    
    asyncio.run(_send())

@app.command()
def workflow(
    domain: str = typer.Argument(..., help="Domaine (communication/design)"),
):
    """Workflow complet : scrape + envoi"""
    
    async def _workflow():
        if domain == "communication":
            scraper = CommunicationScraper()
            topic_id = settings.telegram_communication_topic_id
        elif domain == "design":
            scraper = DesignScraper()
            topic_id = settings.telegram_design_topic_id
        else:
            typer.echo(f"❌ Domaine inconnu: {domain}")
            raise typer.Exit(1)
        
        # Scraping
        print(f"🔄 Workflow complet {domain}")
        jobs = await scraper.scrape()
        
        if not jobs:
            typer.echo(f"❌ Aucune offre trouvée pour {domain}")
            return
        
        # Envoi
        sent_count = await telegram_bot.send_jobs(
            jobs=jobs,
            topic_id=topic_id,
            job_type=domain
        )
        
        typer.echo(f"✅ Workflow terminé: {sent_count}/{len(jobs)} offres envoyées")
    
    asyncio.run(_workflow())

@app.command()
def scheduler():
    """Lance le scheduler principal"""
    from france_chomage.scheduler import main
    
    print("🚀 Lancement du scheduler principal")
    asyncio.run(main())

@app.command()
def info():
    """Affiche les informations de configuration"""
    
    env = detect_environment()
    
    typer.echo("🇫🇷 France Chômage Bot - Configuration")
    typer.echo("=" * 50)
    typer.echo(f"Environnement: {env.value}")
    typer.echo(f"Localisation: {settings.location}")
    typer.echo(f"Résultats demandés: {settings.results_wanted}")
    typer.echo(f"Topic communication: {settings.telegram_communication_topic_id}")
    typer.echo(f"Topic design: {settings.telegram_design_topic_id}")
    typer.echo(f"Heures communication: {settings.communication_hours}")
    typer.echo(f"Heures design: {settings.design_hours}")
    typer.echo(f"Skip jobs initiaux: {settings.skip_init_job}")

@app.command()
def test():
    """Test la configuration Telegram"""
    
    async def _test():
        try:
            # Test basique de connexion
            bot_info = await telegram_bot.bot.get_me()
            typer.echo(f"✅ Bot connecté: @{bot_info.username}")
            
            # Test d'envoi d'un message de test
            test_message = "🧪 Test de connexion - Bot opérationnel"
            
            await telegram_bot.bot.send_message(
                chat_id=settings.telegram_group_id,
                text=test_message
            )
            
            typer.echo("✅ Message de test envoyé avec succès")
            
        except Exception as exc:
            typer.echo(f"❌ Erreur de connexion: {exc}")
            raise typer.Exit(1)
    
    asyncio.run(_test())

if __name__ == "__main__":
    app()
