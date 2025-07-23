# Main help
python -m france_chomage --help

# Job operations  
python -m france_chomage scrape run communication
python -m france_chomage send run design
python -m france_chomage workflow run restauration

# Database management
python -m france_chomage db init
python -m france_chomage db migrate  
python -m france_chomage db status
python -m france_chomage db cleanup --days 90

# Utilities
python -m france_chomage utils info
python -m france_chomage utils test
python -m france_chomage utils update

# Scheduler
python -m france_chomage scheduler