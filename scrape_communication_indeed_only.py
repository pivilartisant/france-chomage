import csv
import json
import time
import random
import os
from jobspy import scrape_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_communication_indeed_only():
    """Scrape communication avec Indeed uniquement (plus fiable en Docker)"""
    
    print("🎯 Utilisation de Indeed uniquement (Docker-friendly)...")
    
    try:
        # results_wanted = int(os.getenv('RESULTS_WANTED'))
        results_wanted = 10
        print(f"🔍 Recherche de {results_wanted} offres de communication...")
        
        # Délai aléatoire pour éviter la détection
        delay = random.uniform(1, 3)
        print(f"⏳ Attente de {delay:.1f}s...")
        time.sleep(delay)
        
        jobs = scrape_jobs(
            site_name=["indeed"],  # LinkedIn seul, plus tolérant
            search_term="communication",
            location="Paris",
            results_wanted=results_wanted,
            country_indeed= 'FRANCE',

            # linkedin_fetch_description=True
        )
        
        if len(jobs) > 0:
            print(f"✅ Indeed: {len(jobs)} offres communication récupérées")
            return jobs
        else:
            print("⚠️ Aucune offre trouvée sur Indeed")
            return None
            
    except Exception as e:
        import traceback
        print(f"❌ Erreur Indeed:")
        print(f"   Type d'erreur: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        traceback.print_exc()
        return None

# Execution
print("🎯 Scraping communication (version Docker)...")
jobs = scrape_communication_indeed_only()

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de communication")
    jobs.to_csv("jobs_communication.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_communication.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_communication.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs_communication.json")

