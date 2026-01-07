# debug_gamma_api.py
"""בודק את מבנה ה-Gamma API כדי להבין איך לקבל token IDs נכונים"""
import requests
import json

# קבלת אירועים פעילים
url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"
print(f"🔍 שולח בקשה ל-Gamma API: {url}")

response = requests.get(url)
if response.status_code != 200:
    print(f"❌ שגיאה: {response.status_code}")
    exit()

data = response.json()
print(f"✅ קיבלתי {len(data)} אירועים")

# בוא נראה את כל ה-tags השונים
all_tags = set()
for event in data:
    tags = event.get('tags', [])
    for tag in tags:
        if isinstance(tag, dict):
            all_tags.add(tag.get('name', ''))
        else:
            all_tags.add(str(tag))

print(f"🏷️  Tags שונים שנמצאו: {sorted(all_tags)}")

# נראה כמה אירועים עם ה-tags שלהם
print("\n📋 דוגמאות לאירועים עם tags:")
for i, event in enumerate(data[:5]):
    title = event.get('title', 'No title')[:50] + "..." if len(event.get('title', '')) > 50 else event.get('title', 'No title')
    tags = event.get('tags', [])
    tag_names = [tag.get('name', '') if isinstance(tag, dict) else str(tag) for tag in tags]
    print(f"  {i+1}. {title}")
    print(f"     Tags: {tag_names}")

# נסה למצוא שוק קריפטו ספציפי - בוא נחפש ב-title
print("\n🔍 מחפש שווקי קריפטו לפי title...")
crypto_events = []
for event in data:
    title = event.get('title', '').lower()
    if any(word in title for word in ['crypto', 'bitcoin', 'btc', 'ethereum', 'eth']):
        crypto_events.append(event)

print(f"🎯 מצאתי {len(crypto_events)} אירועי קריפטו לפי title")

for i, event in enumerate(crypto_events[:3]):  # הצג 3 ראשונים
    print(f"\n📊 אירוע {i+1}: {event.get('title')}")
    if event.get('markets'):
        market = event['markets'][0]
        print(f"   שוק ID: {market.get('id')}")
        print(f"   שאלה: {market.get('question', 'No question')}")
        print(f"   פעיל: {market.get('active')}")
        print(f"   סגור: {market.get('closed')}")

        tokens = market.get('tokens', [])
        print(f"   Tokens: {len(tokens)}")

        for j, token in enumerate(tokens):
            print(f"     Token {j+1}: ID={token.get('token_id')} Outcome={token.get('outcome')} Price={token.get('price')}")

        if 'outcomePrices' in market:
            print(f"   Outcome Prices: {market['outcomePrices']}")
