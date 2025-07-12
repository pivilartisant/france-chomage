#!/usr/bin/env python3
"""
Détecte si on run en Docker ou en local et utilise les bons scripts
"""
import os
import subprocess
import sys

def is_running_in_docker():
    """Détecte si on run dans Docker"""
    # Méthode 1: Vérifier /.dockerenv
    if os.path.exists('/.dockerenv'):
        return True
        
    # Méthode 2: Vérifier les cgroups
    try:
        with open('/proc/1/cgroup', 'r') as f:
            content = f.read()
            if 'docker' in content:
                return True
    except:
        pass
    
    # Méthode 3: Variable d'environnement
    if os.getenv('DOCKER_ENV') == 'true':
        return True
        
    return False

def run_communication_scraper():
    """Lance le bon scraper communication selon l'environnement"""
    if is_running_in_docker():
        print("🐳 Environnement Docker détecté - utilisation LinkedIn seul")
        return subprocess.run([sys.executable, 'scrape_communication_linkedin_only.py'])
    else:
        print("💻 Environnement local détecté - utilisation version stealth")
        return subprocess.run([sys.executable, 'scrape_communication.py'])

def run_design_scraper():
    """Lance le bon scraper design selon l'environnement"""
    if is_running_in_docker():
        print("🐳 Environnement Docker détecté - utilisation LinkedIn seul")
        return subprocess.run([sys.executable, 'scrape_design_linkedin_only.py'])
    else:
        print("💻 Environnement local détecté - utilisation version stealth")
        return subprocess.run([sys.executable, 'scrape_design.py'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "communication":
            run_communication_scraper()
        elif sys.argv[1] == "design":
            run_design_scraper()
        else:
            print("Usage: python detect_environment.py [communication|design]")
    else:
        print("Détection d'environnement:")
        print(f"Docker: {is_running_in_docker()}")
