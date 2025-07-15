#!/usr/bin/env python3
"""
Resume topic creation for failed categories
"""

import yaml
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = '-1002732537874'

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
            
            if error_code == 429:
                # Rate limited - extract retry time
                retry_after = int(error_desc.split('retry after ')[1])
                print(f"⏳ Rate limited. Waiting {retry_after} seconds for '{topic_name}'...")
                time.sleep(retry_after + 1)
                return create_forum_topic(bot_token, chat_id, topic_name)  # Retry
            else:
                print(f"❌ Failed to create topic '{topic_name}': [{error_code}] {error_desc}")
                return None
            
    except Exception as e:
        print(f"❌ Error creating topic '{topic_name}': {e}")
        return None

def format_category_name(category_key: str) -> str:
    """Format category key into a readable topic name"""
    formatted = category_key.replace('_', ' ').title()
    
    name_mapping = {
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
    """Resume topic creation for categories without proper topic IDs"""
    
    # Load current categories
    with open('categories.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    categories = data['categories']
    
    # Find categories that need topics (either missing or have low IDs that suggest failure)
    failed_categories = []
    
    for category_key, category_data in categories.items():
        topic_id = category_data.get('telegram_topic_id')
        
        # Check if topic ID is missing or looks like an old sequential ID
        if not topic_id or topic_id <= 50:  # New topics start from 511+
            failed_categories.append(category_key)
    
    print(f"📝 Found {len(failed_categories)} categories needing topics")
    
    # Create topics for failed categories
    for category_key in failed_categories:
        topic_name = format_category_name(category_key)
        print(f"\n🔄 Creating topic for '{category_key}' as '{topic_name}'...")
        
        topic_id = create_forum_topic(BOT_TOKEN, CHAT_ID, topic_name)
        
        if topic_id:
            # Update the category data
            categories[category_key]['telegram_topic_id'] = topic_id
            
            # Save immediately after each success
            with open('categories.yml', 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
            
            print(f"💾 Updated categories.yml with topic ID {topic_id}")
        
        # Wait between requests
        time.sleep(2)
    
    print("\n🎉 Topic creation process completed!")

if __name__ == "__main__":
    main()
