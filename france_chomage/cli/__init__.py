"""
France Chômage CLI - Main application
"""
import typer
from france_chomage.scheduler import main as scheduler_main

from . import scraping, sending, workflow, database, migration, utils

app = typer.Typer(
    help="🇫🇷 France Chômage Bot - Job scraping and Telegram posting"
)

# Add sub-applications
app.add_typer(scraping.app, name="scrape")
app.add_typer(sending.app, name="send")
app.add_typer(workflow.app, name="workflow")
app.add_typer(database.app, name="db")
app.add_typer(migration.app, name="migrate")
app.add_typer(utils.app, name="utils")


@app.command()
def scheduler():
    """Launch the main scheduler"""
    typer.echo("🚀 Starting main scheduler...")
    scheduler_main()


if __name__ == "__main__":
    app()
