"""
Détection d'environnement et stratégies de scraping
"""
import os
from enum import Enum
from pathlib import Path
from typing import Tuple

class Environment(Enum):
    LOCAL = "local"
    DOCKER = "docker"

class SiteStrategy(Enum):
    """Stratégies de sites selon l'environnement"""
    LOCAL = ("indeed", "linkedin")  # Tous les sites en local
    DOCKER = ("linkedin",)          # LinkedIn seul en Docker (plus fiable)

def detect_environment() -> Environment:
    """Détecte l'environnement d'exécution"""
    
    # Méthode 1: Fichier /.dockerenv
    if Path("/.dockerenv").exists():
        return Environment.DOCKER
        
    # Méthode 2: cgroups Docker
    try:
        cgroup_path = Path("/proc/1/cgroup")
        if cgroup_path.exists():
            content = cgroup_path.read_text()
            if "docker" in content:
                return Environment.DOCKER
    except (OSError, IOError):
        pass
    
    # Méthode 3: Variable d'environnement explicite
    if os.getenv('DOCKER_ENV') == 'true':
        return Environment.DOCKER
        
    return Environment.LOCAL

def get_sites_for_environment() -> Tuple[str, ...]:
    """Retourne les sites à utiliser selon l'environnement"""
    env = detect_environment()
    
    if env == Environment.DOCKER:
        return SiteStrategy.DOCKER.value
    else:
        return SiteStrategy.LOCAL.value

def is_docker() -> bool:
    """Helper pour vérifier si on est en Docker"""
    return detect_environment() == Environment.DOCKER
