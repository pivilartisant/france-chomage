"""
Workflow commands (scrape + send)
"""
import typer
from .shared import validate_domain, get_scraper_class, get_topic_id
from france_chomage.telegram.bot import telegram_bot

app = typer.Typer(help="Complete workflow commands")


@app.command()
def run(domain: str = typer.Argument(..., help="Domain for workflow (communication/design/restauration)")):
    """Complete workflow: scrape + send"""
    import asyncio
    
    async def _workflow():
        domain_validated = validate_domain(domain)
        scraper_class = get_scraper_class(domain_validated)
        scraper = scraper_class()
        topic_id = get_topic_id(domain_validated)
        
        # Scraping
        typer.echo(f"🔄 Running workflow for {domain}...")
        jobs = await scraper.scrape()
        typer.echo(f"📊 {len(jobs)} jobs scraped")
        
        # Sending
        sent_count = await telegram_bot.send_jobs_from_database(
            category=domain_validated,
            topic_id=topic_id
        )
        
        typer.echo(f"✅ Workflow completed: {sent_count} new jobs sent")
    
    asyncio.run(_workflow())
