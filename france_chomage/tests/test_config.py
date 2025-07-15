"""
Tests for the new configuration system (categories.yml only)
"""
import os
import pytest
import tempfile
import yaml
from unittest.mock import patch

from france_chomage.config import Settings


class TestSettingsNew:
    """Tests for the new configuration system"""
    
    def test_settings_basic(self):
        """Test basic configuration without topic IDs"""
        original_env = dict(os.environ)
        
        try:
            # Set minimum required environment variables
            os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
            os.environ['TELEGRAM_GROUP_ID'] = '-1001234567890'
            
            # Clear optional vars to test defaults
            for key in list(os.environ.keys()):
                if key in ['RESULTS_WANTED', 'LOCATION', 'COUNTRY', 'SKIP_INIT_JOB'] or 'TOPIC_ID' in key:
                    del os.environ[key]
            
            settings = Settings()
            
            assert settings.telegram_bot_token == 'test_token'
            assert settings.telegram_group_id == '-1001234567890'
            assert settings.results_wanted == 15  # default
            assert settings.location == "Paris"  # default
            assert settings.country == "FRANCE"  # default
            assert settings.skip_init_job == 0  # default
            assert settings.max_retries == 3
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_settings_from_env(self):
        """Test reading from environment variables (non-topic settings)"""
        original_env = dict(os.environ)
        
        try:
            os.environ.update({
                'TELEGRAM_BOT_TOKEN': 'test_token_123',
                'TELEGRAM_GROUP_ID': '-1009876543210',
                'RESULTS_WANTED': '25',
                'LOCATION': 'Lyon',
                'SKIP_INIT_JOB': '1'
            })
            
            settings = Settings()
            
            assert settings.telegram_bot_token == 'test_token_123'
            assert settings.telegram_group_id == '-1009876543210'
            assert settings.results_wanted == 25
            assert settings.location == 'Lyon'
            assert settings.skip_init_job == 1
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_topic_ids_from_categories(self):
        """Test that topic IDs come from categories.yml"""
        original_env = dict(os.environ)
        
        try:
            os.environ.update({
                'TELEGRAM_BOT_TOKEN': 'test_token',
                'TELEGRAM_GROUP_ID': '-1001234567890',
                # These should be ignored
                'TELEGRAM_COMMUNICATION_TOPIC_ID': '999',
                'TELEGRAM_DESIGN_TOPIC_ID': '888',
            })
            
            # Mock the category manager
            with patch('france_chomage.categories.CategoryManager.get_category') as mock_get:
                mock_category = type('MockCategory', (), {
                    'telegram_topic_id': 511,
                    'enabled': True
                })()
                mock_get.return_value = mock_category
                
                settings = Settings()
                
                # Should use categories.yml values, not env vars
                assert settings.telegram_communication_topic_id == 511
                assert settings.telegram_design_topic_id == 511
                assert settings.telegram_restauration_topic_id == 511
                
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
