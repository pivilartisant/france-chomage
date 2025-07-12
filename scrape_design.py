import csv
import json
import time
import random
import os
from jobspy import scrape_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_design_with_stealth():
    """Scrape design avec techniques anti-détection"""
    
    # User-Agents réalistes pour éviter la détection
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    
    # Proxies publics gratuits (optionnel, peut aider)
    free_proxies = [
        # Tu peux ajouter des proxies gratuits ici si besoin
        # "http://proxy-server:port",
    ]
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"🎨 Tentative {attempt + 1}/{max_retries}...")
            
            # Délai aléatoire pour éviter la détection
            delay = random.uniform(2, 5)
            print(f"⏳ Attente de {delay:.1f}s...")
            time.sleep(delay)
            
            # Paramètres stealth
            results_wanted = int(os.getenv('RESULTS_WANTED'))

            
            jobs = scrape_jobs(
                site_name= ["indeed", "linkedin"], 
                search_term= "design OR graphisme OR artistique OR graphiste",
                location= "Paris",
                results_wanted= results_wanted,
                country_indeed= 'FRANCE',
            )
            
            if len(jobs) > 0:
                print(f"✅ Succès! {len(jobs)} offres design récupérées")
                return jobs
            else:
                print("⚠️ Aucune offre trouvée, nouvelle tentative...")
                
        except Exception as e:
            import traceback
            print(f"❌ Tentative {attempt + 1} échouée:")
            print(f"   Type d'erreur: {type(e).__name__}")
            print(f"   Message: {str(e)}")
            print(f"   Traceback complet:")
            traceback.print_exc()
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10  # Attente progressive
                print(f"⏳ Attente de {wait_time}s avant nouvelle tentative...")
                time.sleep(wait_time)
    
    print("🚫 Toutes les tentatives ont échoué")
    return None

# Execution avec fallback
print("🎨 Scraping design...")
try:
    jobs = scrape_design_with_stealth()
except Exception as e:
    import traceback
    print(f"❌ Erreur critique dans scrape_design_with_stealth:")
    print(f"   Type d'erreur: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print(f"   Traceback complet:")
    traceback.print_exc()
    jobs = None

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de design")
    jobs.to_csv("jobs_design.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_design.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_design.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs_design.json")

