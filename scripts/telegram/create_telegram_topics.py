#!/usr/bin/env python3
"""
Script to create Telegram forum topics for each category and update categories.yml
"""

import yaml
import requests
import time
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_GROUP_ID')

# Convert @username to numeric ID if needed
if CHAT_ID and CHAT_ID.startswith('@'):
    CHAT_ID = '-1002732537874'  # Numeric ID for @FranceChomage

def load_categories(file_path: str) -> Dict[str, Any]:
    """Load categories from YAML file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_categories(file_path: str, categories: Dict[str, Any]) -> None:
    """Save updated categories to YAML file"""
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(categories, file, default_flow_style=False, allow_unicode=True)

def create_forum_topic(bot_token: str, chat_id: str, topic_name: str) -> int:
    """Create a forum topic and return its ID"""
    url = f"https://api.telegram.org/bot{bot_token}/createForumTopic"
    
    payload = {
        'chat_id': chat_id,
        'name': topic_name
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result['ok']:
            topic_id = result['result']['message_thread_id']
            print(f"✅ Created topic '{topic_name}' with ID: {topic_id}")
            return topic_id
        else:
            error_code = result.get('error_code', 'Unknown')
            error_desc = result.get('description', 'Unknown error')
            print(f"❌ Failed to create topic '{topic_name}': [{error_code}] {error_desc}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error creating topic '{topic_name}': {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating topic '{topic_name}': {e}")
        return None

def format_category_name(category_key: str) -> str:
    """Format category key into a readable topic name"""
    # Convert underscores to spaces and capitalize
    formatted = category_key.replace('_', ' ').title()
    
    # Custom formatting for specific categories
    name_mapping = {
        'Rh': 'RH',
        'Ui': 'UI',
        'Ux': 'UX',
        'Btp': 'BTP',
        'Ratp': 'RATP',
        'Sncf': 'SNCF',
        'Jeu Video': 'Jeu Vidéo',
        'Art Culture': 'Art & Culture',
        'Service Client': 'Service Client',
        'Ressources Humaines': 'Ressources Humaines',
        'Recherche Science': 'Recherche & Science',
        'Emploi Accompagnement': 'Emploi & Accompagnement',
        'Services Personne': 'Services à la Personne',
        'Formation Pro': 'Formation Professionnelle',
        'Mines Carrieres': 'Mines & Carrières',
        'Services Publics': 'Services Publics',
        'Patrimoine Culture': 'Patrimoine & Culture',
        'Travaux Manuels': 'Travaux Manuels',
        'Transport Public': 'Transport Public',
        'Cafe Restauration Personnel': 'Café & Restauration',
        'Energie Renouvelable': 'Énergie Renouvelable',
        'Agent Assurance': 'Agent d\'Assurance',
        'Ingenieur Electronique': 'Ingénieur Électronique',
        'Kinesitherapeute': 'Kinésithérapeute',
        'Aide A Domicile': 'Aide à Domicile'
    }
    
    return name_mapping.get(formatted, formatted)

def main():
    """Main function to create topics and update categories"""
    
    # Validate configuration
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Please set TELEGRAM_BOT_TOKEN and TELEGRAM_GROUP_ID in .env file")
        return
    
    print("🚀 Starting topic creation process...")
    
    # Load categories
    categories_file = "categories.yml"
    try:
        data = load_categories(categories_file)
        categories = data['categories']
        print(f"📂 Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Create topics and update IDs
    updated_categories = {}
    
    for category_key, category_data in categories.items():
        topic_name = format_category_name(category_key)
        print(f"\n📝 Creating topic for '{category_key}' as '{topic_name}'...")
        
        # Create the topic
        topic_id = create_forum_topic(BOT_TOKEN, CHAT_ID, topic_name)
        
        if topic_id:
            # Update the category data with new topic ID
            updated_categories[category_key] = category_data.copy()
            updated_categories[category_key]['telegram_topic_id'] = topic_id
        else:
            # Keep original data if topic creation failed
            updated_categories[category_key] = category_data
        
        # Rate limiting - wait longer between requests
        time.sleep(3)
    
    # Save updated categories
    try:
        updated_data = {'categories': updated_categories}
        save_categories(categories_file, updated_data)
        print(f"\n✅ Updated {categories_file} with new topic IDs")
    except Exception as e:
        print(f"❌ Error saving categories: {e}")
    
    print("\n🎉 Topic creation process completed!")

if __name__ == "__main__":
    main()
