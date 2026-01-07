# debug_market_structure.py
"""בודק את מבנה השווקים הפעילים"""
import requests
import json

# קבל שווקים פעילים
url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=5"
print(f"🔍 שולח בקשה: {url}")

response = requests.get(url)
if response.status_code != 200:
    print(f"❌ שגיאה: {response.status_code}")
    exit()

events = response.json()
print(f"✅ קיבלתי {len(events)} אירועים")

# בדוק את המבנה של האירוע הראשון
if events:
    event = events[0]
    print(f"\n📊 אירוע ראשון: {event.get('title', 'No title')}")
    print(f"מפתחות זמינים: {list(event.keys())}")

    markets = event.get('markets', [])
    print(f"שווקים: {len(markets)}")

    if markets:
        market = markets[0]
        print(f"\n🏷️  שוק ראשון:")
        print(f"מפתחות זמינים: {list(market.keys())}")

        # הדפס את כל המידע על השוק
        for key, value in market.items():
            if key == 'tokens':
                tokens = value
                print(f"{key}: {len(tokens)} tokens")
                if tokens:
                    print("  פירוט tokens:")
                    for i, token in enumerate(tokens):
                        print(f"    Token {i+1}: {token}")
            else:
                print(f"{key}: {value}")

        # בדוק אם יש conditionId או משהו דומה
        condition_id = market.get('conditionId') or market.get('condition_id')
        if condition_id:
            print(f"\n🔍 מצאתי conditionId: {condition_id}")

            # נסה לקבל מידע על התנאי
            try:
                condition_url = f"https://clob.polymarket.com/conditions/{condition_id}"
                cond_response = requests.get(condition_url, timeout=5)
                if cond_response.status_code == 200:
                    condition_data = cond_response.json()
                    print(f"✅ Condition data: {condition_data}")
                else:
                    print(f"❌ Condition error: {cond_response.status_code}")
            except Exception as e:
                print(f"❌ Condition exception: {e}")
