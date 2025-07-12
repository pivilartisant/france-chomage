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
        self.telegram_communication_topic_id = int(os.getenv("TELEGRAM_COMMUNICATION_TOPIC_ID"))
        self.telegram_design_topic_id = int(os.getenv("TELEGRAM_DESIGN_TOPIC_ID"))
        
        # Scraping
        self.results_wanted = int(os.getenv("RESULTS_WANTED"))
        self.location = os.getenv("LOCATION", "Paris")
        self.country = os.getenv("COUNTRY", "FRANCE")
        
        # Scheduling  
        self.skip_init_job = int(os.getenv("SKIP_INIT_JOB", "0"))
        self.communication_hours = [17]
        self.design_hours = [18]
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay_base = 10  # seconds
        self.scrape_delay_min = 1.0
        self.scrape_delay_max = 3.0

# Instance globale
settings = Settings()
