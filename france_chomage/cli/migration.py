"""
Database migration management with Alembic
"""
import typer
import subprocess
import sys
from pathlib import Path

app = typer.Typer(help="Database migration management")

def run_alembic_command(command: str, *args):
    """Run an Alembic command"""
    cmd = ["alembic", command] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode != 0:
            typer.echo(f"❌ Alembic command failed: {result.stderr}")
            return False
        else:
            typer.echo(result.stdout)
            return True
    except Exception as e:
        typer.echo(f"❌ Error running Alembic: {e}")
        return False

@app.command()
def current():
    """Show current migration revision"""
    typer.echo("📋 Current database revision:")
    run_alembic_command("current")

@app.command()
def history():
    """Show migration history"""
    typer.echo("📋 Migration history:")
    run_alembic_command("history")

@app.command()
def upgrade(revision: str = "head"):
    """Upgrade database to a revision (default: head)"""
    typer.echo(f"⬆️ Upgrading database to {revision}...")
    if run_alembic_command("upgrade", revision):
        typer.echo("✅ Database upgrade completed")
    else:
        typer.echo("❌ Database upgrade failed")
        raise typer.Exit(1)

@app.command()
def downgrade(revision: str):
    """Downgrade database to a revision"""
    typer.echo(f"⬇️ Downgrading database to {revision}...")
    if run_alembic_command("downgrade", revision):
        typer.echo("✅ Database downgrade completed")
    else:
        typer.echo("❌ Database downgrade failed")
        raise typer.Exit(1)

@app.command()
def revision(
    message: str = typer.Option(..., "--message", "-m", help="Migration message"),
    autogenerate: bool = typer.Option(True, "--autogenerate", help="Auto-generate migration from model changes")
):
    """Create a new migration revision"""
    typer.echo(f"📝 Creating new migration: {message}")
    args = ["revision", "--message", message]
    if autogenerate:
        args.append("--autogenerate")
    
    if run_alembic_command(*args):
        typer.echo("✅ Migration revision created")
    else:
        typer.echo("❌ Migration revision creation failed")
        raise typer.Exit(1)

@app.command()
def stamp(revision: str = "head"):
    """Mark database as being at a specific revision without running migrations"""
    typer.echo(f"🔖 Stamping database at revision {revision}...")
    if run_alembic_command("stamp", revision):
        typer.echo("✅ Database stamped")
    else:
        typer.echo("❌ Database stamping failed")
        raise typer.Exit(1)

@app.command()
def check():
    """Check if database is up to date with migrations"""
    typer.echo("🔍 Checking migration status...")
    
    # Get current revision
    current_result = subprocess.run(
        ["alembic", "current"], 
        capture_output=True, 
        text=True, 
        cwd=Path.cwd()
    )
    
    # Get head revision
    head_result = subprocess.run(
        ["alembic", "heads"], 
        capture_output=True, 
        text=True, 
        cwd=Path.cwd()
    )
    
    if current_result.returncode == 0 and head_result.returncode == 0:
        current_rev = current_result.stdout.strip()
        head_rev = head_result.stdout.strip()
        
        if current_rev and head_rev:
            if current_rev == head_rev:
                typer.echo("✅ Database is up to date")
                return True
            else:
                typer.echo(f"⚠️ Database needs migration: current={current_rev}, head={head_rev}")
                return False
        else:
            typer.echo("⚠️ Database may not be initialized with Alembic")
            return False
    else:
        typer.echo("❌ Error checking migration status")
        return False
