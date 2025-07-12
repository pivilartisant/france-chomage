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
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"🕵️ Tentative {attempt + 1}/{max_retries}...")
            
            # Délai aléatoire pour éviter la détection
            delay = random.uniform(2, 5)
            print(f"⏳ Attente de {delay:.1f}s...")
            time.sleep(delay)
            
            # Paramètres stealth
            results_wanted = int(os.getenv('RESULTS_WANTED'))
            
            jobs = scrape_jobs(
                search_term= "communication",
                site_name= ["indeed", "linkedin"],
                location= "Paris",
                results_wanted= results_wanted,
                country_indeed= 'FRANCE',
                )
            
            if len(jobs) > 0:
                print(f"✅ Succès! {len(jobs)} offres récupérées")
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
print("🎯 Scraping communication...")
try:
    jobs = scrape_with_stealth()
except Exception as e:
    import traceback
    print(f"❌ Erreur critique dans scrape_with_stealth:")
    print(f"   Type d'erreur: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print(f"   Traceback complet:")
    traceback.print_exc()
    jobs = None

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de communication")
    jobs.to_csv("jobs_communication.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_communication.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_communication.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs_communication.json")

