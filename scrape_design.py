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
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"🎨 Tentative {attempt + 1}/{max_retries} avec techniques stealth...")
            
            # Délai aléatoire pour éviter la détection
            delay = random.uniform(2, 5)
            print(f"⏳ Attente de {delay:.1f}s...")
            time.sleep(delay)
            
            # Paramètres stealth
            results_wanted = int(os.getenv('RESULTS_WANTED'))
            scrape_params = {
                'site_name': ["indeed", "linkedin"],  # LinkedIn plus fiable
                'search_term': "design OR graphisme OR artistique OR graphiste",
                'location': "Paris",
                'results_wanted': results_wanted,
                'country_indeed': 'FRANCE',
                'delay': random.uniform(1, 3),  # Délai entre requêtes
            }
            
            jobs = scrape_jobs(**scrape_params)
            
            if len(jobs) > 0:
                print(f"✅ Succès! {len(jobs)} offres design récupérées")
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
print("🎨 Scraping design...")
jobs = scrape_design_with_stealth()

# Sauvegarde
if jobs is not None and len(jobs) > 0:
    print(f"📊 Total: {len(jobs)} offres de design")
    jobs.to_csv("jobs_design.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    
    with open('jobs_design.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))
    
    with open('jobs_design.json', mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print("✅ Offres sauvegardées dans jobs_design.json")

