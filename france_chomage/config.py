"""
Configuration centralisée avec validation Pydantic
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Configuration globale de l'application"""
    
    def __init__(self):
        # Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_group_id = os.getenv("TELEGRAM_GROUP_ID")
        
        # Topic IDs are now managed by CategoryManager
        # These properties are kept for backward compatibility
        self._category_manager = None
        
        # Scraping
        self.results_wanted = int(os.getenv("RESULTS_WANTED", "15"))
        self.location = os.getenv("LOCATION", "Paris")
        self.country = os.getenv("COUNTRY", "FRANCE")
        
        # Scheduling  
        self.skip_init_job = int(os.getenv("SKIP_INIT_JOB", "0"))
        self.update_hours = [20]
        
        # Retry configuration
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay_base = int(os.getenv("RETRY_DELAY_BASE", "10"))  # seconds
        self.scrape_delay_min = float(os.getenv("SCRAPE_DELAY_MIN", "1.0"))
        self.scrape_delay_max = float(os.getenv("SCRAPE_DELAY_MAX", "3.0"))
        
        # Anti-detection settings
        self.force_docker_mode = os.getenv("FORCE_DOCKER_MODE", "0") == "1"  # Force LinkedIn only
        self.indeed_max_results = int(os.getenv("INDEED_MAX_RESULTS", "10"))  # Limit Indeed results
    
    @property
    def category_manager(self):
        """Lazy load category manager"""
        if self._category_manager is None:
            from .categories import category_manager
            self._category_manager = category_manager
        return self._category_manager
    
    @property
    def telegram_communication_topic_id(self) -> int:
        """Get communication topic ID from categories.yml"""
        return self.category_manager.get_topic_id('communication')
    
    @property
    def telegram_design_topic_id(self) -> int:
        """Get design topic ID from categories.yml"""
        return self.category_manager.get_topic_id('design')
    
    @property
    def telegram_restauration_topic_id(self) -> int:
        """Get restauration topic ID from categories.yml"""
        return self.category_manager.get_topic_id('restauration')

# Instance globale
settings = Settings()
