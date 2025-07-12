import schedule
import time
import asyncio
import subprocess
from telegram_bot import JobTelegramBot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_communication_jobs():
    """Scrape et envoie les offres de communication"""
    print("🎯 Lancement des offres communication...")
    
    # Scrape les offres de communication (détection auto environnement)
    print("📡 Scraping communication en cours...")
    result = subprocess.run(['python', 'detect_environment.py', 'communication'])
    if result.returncode != 0:
        print(f"❌ Erreur scraping communication (code: {result.returncode})")
        return
    
    # Envoie sur Telegram
    print("📤 Envoi vers Telegram...")
    result = subprocess.run(['python', 'bot_communication.py'])
    if result.returncode != 0:
        print(f"❌ Erreur envoi communication (code: {result.returncode})")
    else:
        print("✅ Offres communication envoyées")

def run_design_jobs():
    """Scrape et envoie les offres de design"""
    print("🎨 Lancement des offres design...")
    
    # Scrape les offres de design (détection auto environnement)
    print("📡 Scraping design en cours...")
    result = subprocess.run(['python', 'detect_environment.py', 'design'])
    if result.returncode != 0:
        print(f"❌ Erreur scraping design (code: {result.returncode})")
        return
    
    # Envoie sur Telegram
    print("📤 Envoi vers Telegram...")
    result = subprocess.run(['python', 'bot_design.py'])
    if result.returncode != 0:
        print(f"❌ Erreur envoi design (code: {result.returncode})")
    else:
        print("✅ Offres design envoyées")

# Schedule jobs pour communication (9h et 17h)
# schedule.every().day.at("09:00").do(run_communication_jobs)
schedule.every().day.at("17:00").do(run_communication_jobs)

# Schedule jobs pour design (10h et 18h pour éviter la surcharge)
# schedule.every().day.at("10:00").do(run_design_jobs)
schedule.every().day.at("18:00").do(run_design_jobs)

print("🤖 Planificateur démarré.")
print("📅 Communication: 17h")
print("🎨 Design: 18h")
print("\n🚀 Exécution immédiate pour tester...")

# Exécute le flow complet une fois au démarrage (sauf si SKIP_INIT_JOB=1)
if os.getenv('SKIP_INIT_JOB', '0') != '1':
    print("🚀 Exécution immédiate des jobs au démarrage...")
    run_communication_jobs()
    run_design_jobs()
else:
    print("⏭️ Jobs de démarrage ignorés (SKIP_INIT_JOB=1)")

print("\n⏰ Planification activée. Appuyez sur Ctrl+C pour arrêter.")

while True:
    schedule.run_pending()
    time.sleep(60)
