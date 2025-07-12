import csv
import json
import time
import random
import os
from jobspy import scrape_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_design_linkedin_only():
    """Scrape design avec LinkedIn uniquement (plus fiable en Docker)"""
    
    print("🎨 Utilisation de LinkedIn uniquement (Docker-friendly)...")
    
    try:
        results_wanted = int(os.getenv('RESULTS_WANTED', '15'))
        
        # Délai aléatoire pour éviter la détection
        delay = random.uniform(1, 3)
        print(f"⏳ Attente de {delay:.1f}s...")
        time.sleep(delay)
        
        jobs = scrape_jobs(
            site_name=["linkedin"],  # LinkedIn seul, plus tolérant
            search_term="design OR graphisme OR artistique OR graphiste",
            location="Paris",
            results_wanted=results_wanted,
            # linkedin_fetch_description=True,
        )
        
        if len(jobs) > 0:
            print(f"✅ LinkedIn: {len(jobs)} offres design récupérées")
            return jobs
        else:
            print("⚠️ Aucune offre trouvée sur LinkedIn")
            return None
            
    except Exception as e:
        import traceback
        print(f"❌ Erreur LinkedIn:")
        print(f"   Type d'erreur: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        traceback.print_exc()
        return None

# Execution
print("🎨 Scraping design (version Docker)...")
jobs = scrape_design_linkedin_only()

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de design")
    jobs.to_csv("jobs_design.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_design.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_design.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs_design.json")
else:
    print("⚠️ Création d'un fichier vide")
    with open('jobs_design.json', 'w') as f:
        json.dump([], f)
