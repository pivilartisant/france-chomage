import csv
import json
import time
import random
import os
from jobspy import scrape_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_with_stealth():
    """Scrape avec techniques anti-détection"""
    
    # Liste de User-Agents réalistes
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # Proxies publics (optionnel, peut aider)
    proxies = [
        # "http://proxy1:port",
        # "http://proxy2:port",
    ]
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"🕵️ Tentative {attempt + 1}/{max_retries} avec techniques stealth...")
            
            # Délai aléatoire pour éviter la détection
            delay = random.uniform(2, 5)
            print(f"⏳ Attente de {delay:.1f}s...")
            time.sleep(delay)
            
            # Paramètres stealth
            results_wanted = int(os.getenv('RESULTS_WANTED', '10'))
            scrape_params = {
                'site_name': ["indeed"],
                'search_term': "communication",
                'location': "Paris",
                'results_wanted': results_wanted,
                'country_indeed': 'FRANCE',
                'delay': random.uniform(1, 3),  # Délai entre requêtes
            }
            
            # Ajoute proxies si disponibles
            if proxies:
                scrape_params['proxies'] = proxies
            
            jobs = scrape_jobs(**scrape_params)
            
            if len(jobs) > 0:
                print(f"✅ Succès! {len(jobs)} offres récupérées")
                return jobs
            else:
                print("⚠️ Aucune offre trouvée, nouvelle tentative...")
                
        except Exception as e:
            print(f"❌ Tentative {attempt + 1} échouée: {str(e)[:100]}...")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10  # Attente progressive
                print(f"⏳ Attente de {wait_time}s avant nouvelle tentative...")
                time.sleep(wait_time)
    
    print("🚫 Toutes les tentatives ont échoué")
    return None

# Execution avec fallback
print("🎯 Scraping communication avec mode stealth...")
jobs = scrape_with_stealth()

if jobs is None or len(jobs) == 0:
    print("📡 Fallback vers LinkedIn...")
    try:
        results_wanted = int(os.getenv('RESULTS_WANTED', '10'))
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term="communication",
            location="Paris",
            results_wanted=results_wanted,
            linkedin_fetch_description=True,
        )
        print(f"✅ LinkedIn: {len(jobs)} offres")
    except Exception as e:
        print(f"❌ LinkedIn aussi bloqué: {e}")
        jobs = None

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de communication")
    jobs.to_csv("jobs_communication.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_communication.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_communication.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs.json")
else:
    print("⚠️ Création d'un fichier vide")
    with open('jobs.json', 'w') as f:
        json.dump([], f)
