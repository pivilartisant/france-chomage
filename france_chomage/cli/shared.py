"""
Shared types and utilities for CLI
"""
import typer
from france_chomage.config import settings
from france_chomage.categories import category_manager
from france_chomage.scraping.category_scraper import create_category_scraper


def get_valid_domains() -> list[str]:
    """Get list of valid domains from configuration"""
    try:
        return category_manager.get_enabled_category_names()
    except Exception as e:
        typer.echo(f"❌ Error loading categories: {e}")
        # Fallback to hardcoded domains for backward compatibility
        return ["communication", "design", "restauration"]


def validate_domain(domain: str) -> str:
    """Validate domain and return it if valid"""
    valid_domains = get_valid_domains()
    if domain not in valid_domains:
        typer.echo(f"❌ Invalid domain: {domain}")
        typer.echo(f"Valid domains: {', '.join(valid_domains)}")
        raise typer.Exit(1)
    return domain


def get_scraper_class(domain: str):
    """Get scraper class for domain using configuration"""
    try:
        category_config = category_manager.get_category(domain)
        return lambda: create_category_scraper(category_config)
    except Exception as e:
        typer.echo(f"❌ Error getting scraper for {domain}: {e}")
        raise typer.Exit(1)


def get_topic_id(domain: str) -> int:
    """Get Telegram topic ID for domain using configuration"""
    try:
        category_config = category_manager.get_category(domain)
        return category_config.telegram_topic_id
    except Exception as e:
        typer.echo(f"❌ Error getting topic ID for {domain}: {e}")
        raise typer.Exit(1)


# Backward compatibility
VALID_DOMAINS = get_valid_domains()
