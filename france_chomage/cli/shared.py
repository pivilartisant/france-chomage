"""
Shared types and utilities for CLI
"""
import typer
from france_chomage.config import settings

VALID_DOMAINS = ["communication", "design", "restauration"]


def validate_domain(domain: str) -> str:
    """Validate domain and return it if valid"""
    if domain not in VALID_DOMAINS:
        typer.echo(f"❌ Invalid domain: {domain}")
        typer.echo(f"Valid domains: {', '.join(VALID_DOMAINS)}")
        raise typer.Exit(1)
    return domain


def get_scraper_class(domain: str):
    """Get scraper class for domain"""
    from france_chomage.scraping import CommunicationScraper, DesignScraper, RestaurationScraper
    
    scrapers = {
        "communication": CommunicationScraper,
        "design": DesignScraper,
        "restauration": RestaurationScraper,
    }
    return scrapers[domain]


def get_topic_id(domain: str) -> int:
    """Get Telegram topic ID for domain"""
    topic_ids = {
        "communication": settings.telegram_communication_topic_id,
        "design": settings.telegram_design_topic_id,
        "restauration": settings.telegram_restauration_topic_id,
    }
    return topic_ids[domain]
