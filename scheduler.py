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
    
    # Scrape les offres de communication (version stealth en priorité)
    result = subprocess.run(['python', 'flemme_communication_stealth.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur scraping communication: {result.stderr}")
        return
    
    # Envoie sur Telegram
    result = subprocess.run(['python', 'bot_communication.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur envoi communication: {result.stderr}")
    else:
        print("✅ Offres communication envoyées")

def run_design_jobs():
    """Scrape et envoie les offres de design"""
    print("🎨 Lancement des offres design...")
    
    # Scrape les offres de design (version stealth en priorité)
    result = subprocess.run(['python', 'flemme_design_stealth.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur scraping design: {result.stderr}")
        return
    
    # Envoie sur Telegram
    result = subprocess.run(['python', 'bot_design.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur envoi design: {result.stderr}")
    else:
        print("✅ Offres design envoyées")

# Schedule jobs pour communication (9h et 17h)
schedule.every().day.at("09:00").do(run_communication_jobs)
schedule.every().day.at("17:00").do(run_communication_jobs)

# Schedule jobs pour design (10h et 18h pour éviter la surcharge)
schedule.every().day.at("10:00").do(run_design_jobs)
schedule.every().day.at("18:00").do(run_design_jobs)

print("🤖 Planificateur démarré.")
print("📅 Communication: 9h et 17h")
print("🎨 Design: 10h et 18h")
print("\n🚀 Exécution immédiate pour tester...")

# Exécute le flow complet une fois au démarrage
run_communication_jobs()
run_design_jobs()

print("\n⏰ Planification activée. Appuyez sur Ctrl+C pour arrêter.")

while True:
    schedule.run_pending()
    time.sleep(60)
