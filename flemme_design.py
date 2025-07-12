import csv
import json
from jobspy import scrape_jobs

# Scrape des offres de design/graphisme
jobs = scrape_jobs(
    site_name=["indeed"],
    search_term="design graphique",
    location="Paris",
    results_wanted=5,
    country_indeed='FRANCE',
    
    # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
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
