"""
Scraper pour les offres de restauration
"""
from .base import ScraperBase

class RestaurationScraper(ScraperBase):
    """Scraper spécialisé pour les offres de restauration"""
    
    search_terms = "restauration OR cuisinier OR chef OR serveur OR barman OR sommelier OR commis"
    filename_prefix = "restauration"
    job_type = "restauration"
