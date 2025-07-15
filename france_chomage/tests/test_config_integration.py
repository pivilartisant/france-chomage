"""
Integration tests for the new configuration system
"""
import os
import pytest
from unittest.mock import patch

from france_chomage.config import Settings


class TestConfigIntegration:
    """Integration tests for the configuration system"""
    
    def test_backward_compatibility(self):
        """Test that old code still works with new system"""
        original_env = dict(os.environ)
        
        try:
            # Set required env vars
            os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
            os.environ['TELEGRAM_GROUP_ID'] = '-1001234567890'
            
            # Test that we can create settings without categories.yml
            with patch('france_chomage.categories.CategoryManager.load_categories') as mock_load:
                mock_load.side_effect = FileNotFoundError("categories.yml not found")
                
                settings = Settings()
                assert settings.telegram_bot_token == 'test_token'
                assert settings.telegram_group_id == '-1001234567890'
                
                # These should fail gracefully now
                with pytest.raises(FileNotFoundError):
                    _ = settings.telegram_communication_topic_id
                    
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_categories_yml_only(self):
        """Test that only categories.yml is used for topic IDs"""
        original_env = dict(os.environ)
        
        try:
            os.environ.update({
                'TELEGRAM_BOT_TOKEN': 'test_token',
                'TELEGRAM_GROUP_ID': '-1001234567890',
                'TELEGRAM_COMMUNICATION_TOPIC_ID': '999',  # Should be ignored
            })
            
            # Mock the category manager to return a specific value
            with patch('france_chomage.categories.CategoryManager.get_category') as mock_get:
                mock_category = type('MockCategory', (), {
                    'telegram_topic_id': 511,
                    'enabled': True
                })()
                mock_get.return_value = mock_category
                
                settings = Settings()
                # Should use category value (511) and ignore env var (999)
                assert settings.telegram_communication_topic_id == 511
                
        finally:
            os.environ.clear()
            os.environ.update(original_env)
