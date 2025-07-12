"""
Tests pour la configuration
"""
import os
import pytest
from pydantic import ValidationError

from france_chomage.config import Settings

class TestSettings:
    """Tests pour la configuration Settings"""
    
    def test_settings_defaults(self):
        """Test valeurs par défaut"""
        # Sauvegarde les env vars existantes
        original_env = dict(os.environ)
        
        try:
            # Clear env vars pour tester defaults
            for key in list(os.environ.keys()):
                if key.startswith('TELEGRAM_') or key.startswith('RESULTS_'):
                    del os.environ[key]
            
            # Mock des variables obligatoires
            os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
            os.environ['TELEGRAM_GROUP_ID'] = '-1001234567890'
            
            settings = Settings()
            
            assert settings.communication_topic_id == 3
            assert settings.design_topic_id == 40
            assert settings.results_wanted == 15
            assert settings.location == "Paris"
            assert settings.country == "FRANCE"
            assert settings.skip_init_job == False
            assert settings.communication_hours == [9, 17]
            assert settings.design_hours == [10, 18]
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
            assert settings.communication_topic_id == 5
            assert settings.design_topic_id == 42
            assert settings.results_wanted == 25
            assert settings.location == 'Lyon'
            assert settings.skip_init_job == True
            
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
            
            # Test "1" -> True
            os.environ.update({**base_env, 'SKIP_INIT_JOB': '1'})
            settings1 = Settings()
            assert settings1.skip_init_job == True
            
            # Test "0" -> False  
            os.environ.update({**base_env, 'SKIP_INIT_JOB': '0'})
            settings2 = Settings()
            assert settings2.skip_init_job == False
            
            # Test "true" -> True
            os.environ.update({**base_env, 'SKIP_INIT_JOB': 'true'})
            settings3 = Settings()
            assert settings3.skip_init_job == True
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_results_wanted_validation(self):
        """Test validation de results_wanted"""
        original_env = dict(os.environ)
        
        try:
            base_env = {
                'TELEGRAM_BOT_TOKEN': 'test',
                'TELEGRAM_GROUP_ID': '-1001234567890'
            }
            
            # Test valeur négative
            os.environ.update({**base_env, 'RESULTS_WANTED': '-5'})
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "results_wanted must be positive" in str(exc_info.value)
            
            # Test valeur trop élevée
            os.environ.update({**base_env, 'RESULTS_WANTED': '150'})
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "results_wanted should not exceed 100" in str(exc_info.value)
            
            # Test valeur valide
            os.environ.update({**base_env, 'RESULTS_WANTED': '30'})
            settings = Settings()
            assert settings.results_wanted == 30
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_required_fields(self):
        """Test que les champs obligatoires sont validés"""
        original_env = dict(os.environ)
        
        try:
            # Clear all env vars
            os.environ.clear()
            
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            required_fields = {error["loc"][0] for error in errors}
            
            assert "telegram_bot_token" in required_fields
            assert "telegram_group_id" in required_fields
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
