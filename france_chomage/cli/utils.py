"""
Utility commands
"""
import typer
from pathlib import Path
import json

from france_chomage.config import settings
from france_chomage.environments import detect_environment
from france_chomage.telegram.bot import telegram_bot

app = typer.Typer(help="Utility commands")


@app.command()
def info():
    """Show configuration information"""
    env = detect_environment()
    
    typer.echo("🇫🇷 France Chômage Bot - Configuration")
    typer.echo("=" * 50)
    typer.echo(f"Environment: {env.value}")
    typer.echo(f"Location: {settings.location}")
    typer.echo(f"Results wanted: {settings.results_wanted}")
    typer.echo(f"Group ID: {settings.telegram_group_id}")
    typer.echo(f"Skip initial jobs: {settings.skip_init_job}")
    typer.echo()
    
    # Show category information
    try:
        categories = settings.category_manager.get_enabled_categories()
        typer.echo("📂 Enabled Categories:")
        for name, category in categories.items():
            topic_id = settings.category_manager.get_topic_id(name)
            scrape_times = ', '.join([f"{h:02d}:00" for h in category.scrape_hours])
            send_times = ', '.join([f"{h:02d}:00" for h in category.send_hours])
            typer.echo(f"  {name}: Topic ID {topic_id}")
            typer.echo(f"    Scrape: {scrape_times}")
            typer.echo(f"    Send: {send_times}")
    except Exception as e:
        typer.echo(f"❌ Error loading categories: {e}")
        
    typer.echo()
    typer.echo("📊 Main Categories:")
    try:
        typer.echo(f"  Communication: {settings.telegram_communication_topic_id}")
        typer.echo(f"  Design: {settings.telegram_design_topic_id}")
        typer.echo(f"  Restauration: {settings.telegram_restauration_topic_id}")
    except Exception as e:
        typer.echo(f"  ❌ Error: {e}")


@app.command()
def test():
    """Test Telegram configuration"""
    import asyncio
    
    async def _test():
        try:
            # Test basic connection
            bot_info = await telegram_bot.bot.get_me()
            typer.echo(f"✅ Bot connected: @{bot_info.username}")
            
            # Test sending a message
            test_message = "🧪 Test connection - Bot operational"
            
            await telegram_bot.bot.send_message(
                chat_id=settings.telegram_group_id,
                text=test_message
            )
            
            typer.echo("✅ Test message sent successfully")
            
        except Exception as exc:
            typer.echo(f"❌ Connection error: {exc}")
            raise typer.Exit(1)
    
    asyncio.run(_test())


@app.command()
def update():
    """Send status summary to general topic"""
    import asyncio
    
    async def _update():
        updates = {}
        
        # Get all enabled categories
        try:
            enabled_categories = settings.category_manager.get_enabled_category_names()
        except Exception as e:
            typer.echo(f"❌ Error loading categories: {e}")
            return
        
        # Query database for job counts by category
        from france_chomage.database import connection
        from france_chomage.database.repository import JobRepository
        
        try:
            connection.initialize_database()
            if connection.async_session_factory is None:
                raise RuntimeError("Database not properly initialized")
                
            async with connection.async_session_factory() as session:
                repository = JobRepository(session)
                
                for category in enabled_categories:
                    try:
                        # Get jobs from database (last 30 days)
                        jobs = await repository.get_jobs_by_category(category, days_limit=30)
                        job_count = len(jobs)
                        updates[category] = {'jobs_sent': job_count}
                        typer.echo(f"💾 {category}: {job_count} jobs in database")
                        
                    except Exception as e:
                        updates[category] = {'jobs_sent': 0, 'error': f"Database query error: {e}"}
                        typer.echo(f"❌ Error querying {category}: {e}")
                        
        except Exception as e:
            typer.echo(f"❌ Database connection error: {e}")
            return
        
        if updates:
            typer.echo("📊 Sending status summary...")
            success = await telegram_bot.send_update_summary(updates)
            if success:
                typer.echo("✅ Status summary sent")
            else:
                typer.echo("❌ Error sending summary")
        else:
            typer.echo("⚠️ No data to send")
    
    asyncio.run(_update())
