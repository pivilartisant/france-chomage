"""
Configuration-driven category scraper
"""
from typing import List, Optional
from france_chomage.categories import CategoryConfig
from .base import ScraperBase
from france_chomage.models import Job


class CategoryScraper(ScraperBase):
    """Generic scraper that works with any category configuration"""
    
    def __init__(self, category_config: CategoryConfig):
        super().__init__()
        self.category_config = category_config
        
        # Set required attributes from configuration
        self.search_terms = category_config.search_terms
        self.filename_prefix = category_config.name
        self.job_type = category_config.name
        
        # Apply category-specific overrides
        if category_config.max_results:
            self._override_max_results = category_config.max_results
    
    async def scrape(self) -> List[Job]:
        """Scrape jobs for this category"""
        print(f"🎯 Scraping category: {self.category_config.name}")
        print(f"🔍 Search terms: {self.search_terms}")
        
        # Temporarily override results_wanted if configured
        original_results_wanted = None
        if hasattr(self, '_override_max_results'):
            from france_chomage.config import settings
            original_results_wanted = settings.results_wanted
            settings.results_wanted = self._override_max_results
            print(f"📊 Using custom max results: {self._override_max_results}")
        
        try:
            jobs = await super().scrape()
            return jobs
        finally:
            # Restore original setting
            if original_results_wanted is not None:
                from france_chomage.config import settings
                settings.results_wanted = original_results_wanted


class CategoryScraperFactory:
    """Factory for creating category scrapers"""
    
    @staticmethod
    def create_scraper(category_config: CategoryConfig) -> ScraperBase:
        """Create appropriate scraper for the category"""
        
        # If a custom scraper class is specified, try to load it
        if category_config.custom_scraper_class:
            try:
                scraper_class = CategoryScraperFactory._load_custom_scraper(
                    category_config.custom_scraper_class
                )
                return scraper_class(category_config)
            except Exception as e:
                print(f"⚠️ Failed to load custom scraper {category_config.custom_scraper_class}: {e}")
                print("🔄 Falling back to generic CategoryScraper")
        
        # Default to generic CategoryScraper
        return CategoryScraper(category_config)
    
    @staticmethod
    def _load_custom_scraper(class_name: str):
        """Dynamically load a custom scraper class"""
        # Try to import from the scraping module
        try:
            from france_chomage.scraping import custom_scrapers
            return getattr(custom_scrapers, class_name)
        except (ImportError, AttributeError):
            # Try to import directly from scraping package
            module_name = f"france_chomage.scraping.{class_name.lower()}"
            import importlib
            module = importlib.import_module(module_name)
            return getattr(module, class_name)


# Convenience function for creating scrapers
def create_category_scraper(category_config: CategoryConfig) -> ScraperBase:
    """Create a scraper for the given category configuration"""
    return CategoryScraperFactory.create_scraper(category_config)
