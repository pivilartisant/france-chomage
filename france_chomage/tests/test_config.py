"""
Tests pour la configuration
"""
import os
import pytest

from france_chomage.config import Settings

class TestSettings:
    """Tests pour la configuration Settings"""
    
    def test_settings_with_defaults(self):
        """Test configuration avec valeurs par défaut"""
        # Sauvegarde les env vars existantes
        original_env = dict(os.environ)
        
        try:
            # Set minimum required environment variables
            os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
            os.environ['TELEGRAM_GROUP_ID'] = '-1001234567890'
            # Remove optional vars to test defaults
            for key in ['TELEGRAM_COMMUNICATION_TOPIC_ID', 'TELEGRAM_DESIGN_TOPIC_ID', 
                       'RESULTS_WANTED', 'LOCATION', 'COUNTRY', 'SKIP_INIT_JOB']:
                if key in os.environ:
                    del os.environ[key]
            
            settings = Settings()
            
            assert settings.telegram_bot_token == 'test_token'
            assert settings.telegram_group_id == '-1001234567890'
            assert settings.telegram_communication_topic_id == 3  # default
            assert settings.telegram_design_topic_id == 40  # default
            assert settings.results_wanted == 15  # default
            assert settings.location == "Paris"  # default
            assert settings.country == "FRANCE"  # default
            assert settings.skip_init_job == 0  # default
            assert settings.communication_hours == [17]
            assert settings.design_hours == [18]
            assert settings.max_retries == 3
            
        finally:
            # Restore env vars
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_settings_from_env(self):
        """Test lecture depuis variables d'environnement"""
        original_env = dict(os.environ)
        
        try:
            os.environ.update({
                'TELEGRAM_BOT_TOKEN': 'test_token_123',
                'TELEGRAM_GROUP_ID': '-1009876543210',
                'TELEGRAM_COMMUNICATION_TOPIC_ID': '5',
                'TELEGRAM_DESIGN_TOPIC_ID': '42',
                'RESULTS_WANTED': '25',
                'LOCATION': 'Lyon',
                'SKIP_INIT_JOB': '1'
            })
            
            settings = Settings()
            
            assert settings.telegram_bot_token == 'test_token_123'
            assert settings.telegram_group_id == '-1009876543210'
            assert settings.telegram_communication_topic_id == 5
            assert settings.telegram_design_topic_id == 42
            assert settings.results_wanted == 25
            assert settings.location == 'Lyon'
            assert settings.skip_init_job == 1
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_skip_init_job_parsing(self):
        """Test parsing SKIP_INIT_JOB"""
        original_env = dict(os.environ)
        
        try:
            base_env = {
                'TELEGRAM_BOT_TOKEN': 'test',
                'TELEGRAM_GROUP_ID': '-1001234567890'
            }
            
            # Test "0" -> 0  
            os.environ.update({**base_env, 'SKIP_INIT_JOB': '0'})
            settings2 = Settings()
            assert settings2.skip_init_job == 0
            
            # Test "1" -> 1
            os.environ.update({**base_env, 'SKIP_INIT_JOB': '1'})
            settings3 = Settings()
            assert settings3.skip_init_job == 1
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_basic_functionality(self):
        """Test fonctionnalité de base"""
        original_env = dict(os.environ)
        
        try:
            base_env = {
                'TELEGRAM_BOT_TOKEN': 'test',
                'TELEGRAM_GROUP_ID': '-1001234567890',
                'RESULTS_WANTED': '30'
            }
            
            os.environ.update(base_env)
            settings = Settings()
            
            # Test que les valeurs sont correctement lues
            assert settings.telegram_bot_token == 'test'
            assert settings.telegram_group_id == '-1001234567890' 
            assert settings.results_wanted == 30
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
