#!/usr/bin/env python3
"""
Script to get the numeric chat ID from a Telegram group username
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_USERNAME = os.getenv('TELEGRAM_GROUP_ID')

def get_chat_id(bot_token: str, chat_username: str) -> str:
    """Get numeric chat ID from username"""
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    
    payload = {
        'chat_id': chat_username
    }
    
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        
        result = response.json()
        if result['ok']:
            chat_id = result['result']['id']
            chat_type = result['result']['type']
            title = result['result'].get('title', 'Unknown')
            
            print(f"✅ Chat found:")
            print(f"   Title: {title}")
            print(f"   Type: {chat_type}")
            print(f"   Numeric ID: {chat_id}")
            
            # Check if it's a forum group
            is_forum = result['result'].get('is_forum', False)
            print(f"   Is Forum: {is_forum}")
            
            if not is_forum:
                print("⚠️  WARNING: This group doesn't have forum topics enabled!")
                print("   You need to enable forum topics in the group settings.")
            
            return str(chat_id)
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_USERNAME:
        print("❌ Please set TELEGRAM_BOT_TOKEN and TELEGRAM_GROUP_ID in .env file")
    else:
        print(f"🔍 Getting chat info for {CHAT_USERNAME}...")
        chat_id = get_chat_id(BOT_TOKEN, CHAT_USERNAME)
