"""
Workflow commands (scrape + send)
"""
import typer
from .shared import validate_domain, get_scraper_class, get_topic_id
from france_chomage.telegram.bot import telegram_bot

app = typer.Typer(help="Complete workflow commands")


@app.command()
def scrape(domain: str = typer.Argument(..., help="Domain for scraping (communication/design/restauration)")):
    """Scrape jobs only (no sending)"""
    import asyncio
    
    async def _scrape():
        domain_validated = validate_domain(domain)
        scraper_class = get_scraper_class(domain_validated)
        scraper = scraper_class()
        
        # Scraping only
        typer.echo(f"🔍 Scraping {domain}...")
        jobs = await scraper.scrape()
        typer.echo(f"📊 {len(jobs)} jobs scraped and saved to database")
    
    asyncio.run(_scrape())


@app.command()
def send(domain: str = typer.Argument(..., help="Domain for sending (communication/design/restauration)")):
    """Send jobs only (no scraping)"""
    import asyncio
    
    async def _send():
        domain_validated = validate_domain(domain)
        topic_id = get_topic_id(domain_validated)
        
        # Sending only
        typer.echo(f"📤 Sending {domain} jobs from database...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category=domain_validated,
            topic_id=topic_id
        )
        
        typer.echo(f"✅ {sent_count} new jobs sent")
    
    asyncio.run(_send())


@app.command()
def run(domain: str = typer.Argument(..., help="Domain for workflow (communication/design/restauration)")):
    """Complete workflow: scrape + send (separated operations)"""
    import asyncio
    
    async def _workflow():
        domain_validated = validate_domain(domain)
        scraper_class = get_scraper_class(domain_validated)
        scraper = scraper_class()
        topic_id = get_topic_id(domain_validated)
        
        # Phase 1: Scraping
        typer.echo(f"🔄 Running separated workflow for {domain}...")
        typer.echo(f"🔍 Phase 1: Scraping...")
        jobs = await scraper.scrape()
        typer.echo(f"📊 {len(jobs)} jobs scraped and saved to database")
        
        # Phase 2: Sending
        typer.echo(f"📤 Phase 2: Sending...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category=domain_validated,
            topic_id=topic_id
        )
        
        typer.echo(f"✅ Workflow completed: {sent_count} new jobs sent")
    
    asyncio.run(_workflow())
