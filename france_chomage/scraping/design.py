"""
Scraper pour les offres de design
"""
from .base import ScraperBase

class DesignScraper(ScraperBase):
    """Scraper spécialisé pour les offres de design"""
    
    search_terms = "design graphique OR graphiste OR UI UX OR designer"
    filename_prefix = "design"
    job_type = "design"
