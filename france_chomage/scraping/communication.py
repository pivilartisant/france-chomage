"""
Scraper pour les offres de communication
"""
from .base import ScraperBase

class CommunicationScraper(ScraperBase):
    """Scraper spécialisé pour les offres de communication"""
    
    search_terms = "communication"
    filename_prefix = "communication"
    job_type = "communication"
