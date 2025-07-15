#!/usr/bin/env python3
"""
Test bot permissions in the Telegram group
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = '-1002732537874'  # Numeric ID for @FranceChomage

def test_bot_permissions():
    """Test if bot has necessary permissions"""
    
    # Test 1: Get chat member (bot itself)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    payload = {
        'chat_id': CHAT_ID,
        'user_id': BOT_TOKEN.split(':')[0]  # Bot's user ID from token
    }
    
    try:
        response = requests.get(url, params=payload)
        result = response.json()
        
        if result['ok']:
            member = result['result']
            status = member['status']
            print(f"✅ Bot status in group: {status}")
            
            if status == 'administrator':
                permissions = member.get('can_manage_topics', False)
                print(f"   Can manage topics: {permissions}")
                
                if not permissions:
                    print("❌ Bot needs 'Manage Topics' permission!")
                    return False
            else:
                print("❌ Bot must be an administrator to create topics!")
                return False
        else:
            print(f"❌ Error checking bot permissions: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_simple_topic_creation():
    """Test creating a simple topic"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createForumTopic"
    
    payload = {
        'chat_id': CHAT_ID,
        'name': 'Test Topic'
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result['ok']:
            topic_id = result['result']['message_thread_id']
            print(f"✅ Test topic created with ID: {topic_id}")
            return topic_id
        else:
            error_code = result.get('error_code', 'Unknown')
            error_desc = result.get('description', 'Unknown error')
            print(f"❌ Failed to create test topic: [{error_code}] {error_desc}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing bot permissions...")
    
    if test_bot_permissions():
        print("\n🧪 Testing topic creation...")
        test_simple_topic_creation()
    else:
        print("\n❌ Bot permissions insufficient. Please:")
        print("   1. Make the bot an administrator in the group")
        print("   2. Give it 'Manage Topics' permission")
