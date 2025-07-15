"""
Database management commands
"""
import typer
from france_chomage.database import (
    create_tables_if_not_exist,
    migrate_all_json_files,
    get_migration_status,
    print_migration_status,
    job_manager
)
from france_chomage.database import connection

app = typer.Typer(help="Database management commands")


@app.command()
def init():
    """Initialize database tables"""
    try:
        from france_chomage.database.migration_utils import create_tables_sync
        create_tables_sync()
        typer.echo("✅ Database initialized")
    except Exception as exc:
        typer.echo(f"❌ Initialization error: {exc}")
        raise typer.Exit(1)


@app.command()
def migrate():
    """Migrate existing JSON files to database"""
    import asyncio
    
    async def _migrate():
        try:
            # Initialize database first
            await create_tables_if_not_exist()
            
            # Migrate JSON files
            connection.initialize_database()
            
            if connection.async_session_factory is None:
                raise RuntimeError("Database not properly initialized")
            
            async with connection.async_session_factory() as session:
                results = await migrate_all_json_files(session)
            
            typer.echo("✅ Migration completed:")
            for category, count in results.items():
                typer.echo(f"  - {category}: {count} jobs migrated")
                
        except Exception as exc:
            typer.echo(f"❌ Migration error: {exc}")
            raise typer.Exit(1)
    
    asyncio.run(_migrate())


@app.command()
def status():
    """Show database status and statistics"""
    import asyncio
    
    async def _status():
        try:
            connection.initialize_database()
            
            if connection.async_session_factory is None:
                raise RuntimeError("Database not properly initialized")
            
            async with connection.async_session_factory() as session:
                stats = await get_migration_status(session)
            
            print_migration_status(stats)
            
        except Exception as exc:
            typer.echo(f"❌ Status error: {exc}")
            raise typer.Exit(1)
    
    asyncio.run(_status())


@app.command()
def cleanup(
    days: int = typer.Option(90, help="Days to keep (default: 90)")
):
    """Clean up old jobs from database"""
    import asyncio
    
    async def _cleanup():
        try:
            removed_count = await job_manager.cleanup_old_jobs(days)
            typer.echo(f"✅ {removed_count} old jobs removed (>{days} days)")
        except Exception as exc:
            typer.echo(f"❌ Cleanup error: {exc}")
            raise typer.Exit(1)
    
    asyncio.run(_cleanup())
