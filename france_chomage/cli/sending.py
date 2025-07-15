"""
Telegram sending commands
"""
import typer
from .shared import validate_domain, get_topic_id
from france_chomage.telegram.bot import telegram_bot

app = typer.Typer(help="Telegram sending commands")


@app.command()
def run(domain: str = typer.Argument(..., help="Domain to send (communication/design/restauration)")):
    """Send job offers to Telegram"""
    import asyncio
    
    async def _send():
        domain_validated = validate_domain(domain)
        topic_id = get_topic_id(domain_validated)
        
        typer.echo(f"📤 Sending {domain} jobs from database...")
        
        sent_count = await telegram_bot.send_jobs_from_database(
            category=domain_validated,
            topic_id=topic_id
        )
        
        typer.echo(f"✅ {sent_count} new jobs sent")
    
    asyncio.run(_send())
