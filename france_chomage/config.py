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
        self.telegram_communication_topic_id = int(os.getenv("TELEGRAM_COMMUNICATION_TOPIC_ID", "3"))
        self.telegram_design_topic_id = int(os.getenv("TELEGRAM_DESIGN_TOPIC_ID", "40"))
        self.telegram_restauration_topic_id = int(os.getenv("TELEGRAM_RESTAURATION_TOPIC_ID", "326"))
        
        # Scraping
        self.results_wanted = int(os.getenv("RESULTS_WANTED", "15"))
        self.location = os.getenv("LOCATION", "Paris")
        self.country = os.getenv("COUNTRY", "FRANCE")
        
        # Scheduling  
        self.skip_init_job = int(os.getenv("SKIP_INIT_JOB", "0"))
        self.communication_hours = [17]
        self.design_hours = [18]
        self.restauration_hours = [19]
        
        # Retry configuration
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay_base = int(os.getenv("RETRY_DELAY_BASE", "10"))  # seconds
        self.scrape_delay_min = float(os.getenv("SCRAPE_DELAY_MIN", "1.0"))
        self.scrape_delay_max = float(os.getenv("SCRAPE_DELAY_MAX", "3.0"))
        
        # Anti-detection settings
        self.force_docker_mode = os.getenv("FORCE_DOCKER_MODE", "0") == "1"  # Force LinkedIn only
        self.indeed_max_results = int(os.getenv("INDEED_MAX_RESULTS", "10"))  # Limit Indeed results

# Instance globale
settings = Settings()
