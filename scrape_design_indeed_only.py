import csv
import json
import time
import random
import os
from jobspy import scrape_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_design_indeed_only():
    """Scrape design avec Indeed uniquement (plus fiable en Docker)"""
    
    print("🎨 Utilisation de Indeed uniquement (Docker-friendly)...")
    
    try:
        # results_wanted = int(os.getenv('RESULTS_WANTED', '15'))
        results_wanted = 10
        print(f"🔍 Recherche de {results_wanted} offres de design...")
        
        # Délai aléatoire pour éviter la détection
        delay = random.uniform(1, 3)
        print(f"⏳ Attente de {delay:.1f}s...")
        time.sleep(delay)
        
        jobs = scrape_jobs(
            site_name=["indeed"],  # LinkedIn seul, plus tolérant
            search_term=" graphiste UI UX  designer ",
            location="Paris",
            results_wanted=results_wanted,
            country_indeed= 'FRANCE',
            # linkedin_fetch_description=True,
        )
        
        if len(jobs) > 0:
            print(f"✅ Indeed: {len(jobs)} offres design récupérées")
            return jobs
        else:
            print("⚠️ Aucune offre trouvée sur LinkedIn")
            return None
            
    except Exception as e:
        import traceback
        print(f"❌ Erreur Indeed:")
        print(f"   Type d'erreur: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        traceback.print_exc()
        return None

# Execution
print("🎨 Scraping design (version Docker)...")
jobs = scrape_design_indeed_only()

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de design")
    jobs.to_csv("jobs_design.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_design.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_design.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs_design.json")

