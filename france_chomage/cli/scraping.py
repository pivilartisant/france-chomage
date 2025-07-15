"""
Scraping commands
"""
import typer
from .shared import validate_domain, get_scraper_class

app = typer.Typer(help="Job scraping commands")


@app.command()
def run(domain: str = typer.Argument(..., help="Domain to scrape (communication/design/restauration)")):
    """Scrape job offers for a domain"""
    import asyncio
    
    async def _scrape():
        domain_validated = validate_domain(domain)
        scraper_class = get_scraper_class(domain_validated)
        scraper = scraper_class()
        
        typer.echo(f"🔍 Scraping {domain} jobs...")
        jobs = await scraper.scrape()
        
        typer.echo(f"✅ {len(jobs)} jobs found for {domain}")
    
    asyncio.run(_scrape())
