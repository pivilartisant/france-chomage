import csv
import json
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "linkedin"],
    search_term="communication",
    location="Paris",
    results_wanted=20,
    country_indeed='FRANCE',
    
    # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel

with open('jobs.csv', mode='r', newline='', encoding='utf-8') as csvfile:
    data = list(csv.DictReader(csvfile))

with open('jobs.json', mode='w', encoding='utf-8') as jsonfile:
    json.dump(data, jsonfile, indent=4)