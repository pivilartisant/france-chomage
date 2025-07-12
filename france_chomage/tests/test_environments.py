"""
Tests pour la détection d'environnement
"""
import os
import pytest
from unittest.mock import patch, mock_open

from france_chomage.environments import (
    detect_environment,
    Environment,
    get_sites_for_environment,
    is_docker,
    SiteStrategy
)

class TestEnvironments:
    """Tests pour la détection d'environnement"""
    
    @patch('france_chomage.environments.Path')
    def test_detect_environment_dockerenv_file(self, mock_path):
        """Test détection via fichier /.dockerenv"""
        mock_path.return_value.exists.return_value = True
        
        env = detect_environment()
        assert env == Environment.DOCKER
    
    @patch('france_chomage.environments.Path')
    def test_detect_environment_cgroups(self, mock_path):
        """Test détection via cgroups"""
        # Mock /.dockerenv n'existe pas
        mock_path_dockerenv = mock_path.return_value
        mock_path_dockerenv.exists.return_value = False
        
        # Mock /proc/1/cgroup avec contenu docker
        mock_path_cgroup = mock_path.return_value
        mock_path_cgroup.exists.return_value = True
        mock_path_cgroup.read_text.return_value = "docker-container-id"
        
        env = detect_environment()
        assert env == Environment.DOCKER
    
    @patch.dict(os.environ, {'DOCKER_ENV': 'true'})
    @patch('france_chomage.environments.Path')
    def test_detect_environment_env_var(self, mock_path):
        """Test détection via variable d'environnement"""
        mock_path.return_value.exists.return_value = False
        
        env = detect_environment()
        assert env == Environment.DOCKER
    
    @patch('france_chomage.environments.Path')
    def test_detect_environment_local(self, mock_path):
        """Test détection environnement local"""
        mock_path.return_value.exists.return_value = False
        
        env = detect_environment()
        assert env == Environment.LOCAL
    
    @patch('france_chomage.environments.detect_environment')
    def test_get_sites_for_docker(self, mock_detect):
        """Test sélection de sites pour Docker"""
        mock_detect.return_value = Environment.DOCKER
        
        sites = get_sites_for_environment()
        assert sites == ("linkedin",)
    
    @patch('france_chomage.environments.detect_environment')
    def test_get_sites_for_local(self, mock_detect):
        """Test sélection de sites pour local"""
        mock_detect.return_value = Environment.LOCAL
        
        sites = get_sites_for_environment()
        assert sites == ("indeed", "linkedin")
    
    @patch('france_chomage.environments.detect_environment')
    def test_is_docker_true(self, mock_detect):
        """Test is_docker helper - Docker"""
        mock_detect.return_value = Environment.DOCKER
        
        assert is_docker() == True
    
    @patch('france_chomage.environments.detect_environment')
    def test_is_docker_false(self, mock_detect):
        """Test is_docker helper - Local"""
        mock_detect.return_value = Environment.LOCAL
        
        assert is_docker() == False
    
    def test_site_strategy_enum(self):
        """Test énumération SiteStrategy"""
        assert SiteStrategy.LOCAL.value == ("indeed", "linkedin")
        assert SiteStrategy.DOCKER.value == ("linkedin",)
    
    def test_environment_enum(self):
        """Test énumération Environment"""
        assert Environment.LOCAL.value == "local"
        assert Environment.DOCKER.value == "docker"
    
    @patch('france_chomage.environments.Path')
    def test_cgroups_exception_handling(self, mock_path):
        """Test gestion des exceptions lors de la lecture cgroups"""
        # Mock /.dockerenv n'existe pas
        mock_path_dockerenv = mock_path.return_value
        mock_path_dockerenv.exists.return_value = False
        
        # Mock exception lors de la lecture de cgroups
        mock_path_cgroup = mock_path.return_value
        mock_path_cgroup.exists.return_value = True
        mock_path_cgroup.read_text.side_effect = OSError("Permission denied")
        
        # Doit fallback sur LOCAL sans crasher
        env = detect_environment()
        assert env == Environment.LOCAL
