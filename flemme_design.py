import csv
import json
import os
from jobspy import scrape_jobs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scrape des offres de design/graphisme
results_wanted = int(os.getenv('RESULTS_WANTED', '10'))
jobs = scrape_jobs(
    site_name=["linkedin"],  # LinkedIn plus fiable
    search_term="design graphique OR graphiste OR UI UX OR designer",
    location="Paris",
    results_wanted=results_wanted,
    linkedin_fetch_description=True,
    
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Trouvé {len(jobs)} offres de design")
print(jobs.head())
jobs.to_csv("jobs_design.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

# Conversion en JSON
with open('jobs_design.csv', mode='r', newline='', encoding='utf-8') as csvfile:
    data = list(csv.DictReader(csvfile))

with open('jobs_design.json', mode='w', encoding='utf-8') as jsonfile:
    json.dump(data, jsonfile, indent=4)

print("Offres de design sauvegardées dans jobs_design.json")
