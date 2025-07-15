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
    typer.echo(f"Communication topic: {settings.telegram_communication_topic_id}")
    typer.echo(f"Design topic: {settings.telegram_design_topic_id}")
    typer.echo(f"Restauration topic: {settings.telegram_restauration_topic_id}")
    typer.echo(f"Group ID: {settings.telegram_group_id}")
    typer.echo(f"Communication hours: {settings.communication_hours}")
    typer.echo(f"Design hours: {settings.design_hours}")
    typer.echo(f"Restauration hours: {settings.restauration_hours}")
    typer.echo(f"Skip initial jobs: {settings.skip_init_job}")


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
        categories = ['communication', 'design', 'restauration']
        
        for category in categories:
            file_path = Path(f"jobs_{category}.json")
            if file_path.exists():
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    job_count = len(data) if isinstance(data, list) else 0
                    updates[category] = {'jobs_sent': job_count}
                    typer.echo(f"📁 {category}: {job_count} jobs in file")
                    
                except Exception as e:
                    updates[category] = {'jobs_sent': 0, 'error': f"File read error: {e}"}
                    typer.echo(f"❌ Error reading {category}: {e}")
            else:
                updates[category] = {'jobs_sent': 0, 'error': 'File not found'}
                typer.echo(f"⚠️ File jobs_{category}.json not found")
        
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
