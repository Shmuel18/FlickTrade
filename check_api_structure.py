# check_api_structure.py
"""בודק את המבנה האמיתי של ה-API"""
import requests
import json

url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=5"

print("🔍 מושך 5 אירועים ראשונים...")
response = requests.get(url, timeout=15)
events = response.json()

print(f"\n📊 קיבלתי {len(events)} אירועים")

# בוא נבדוק את האירוע הראשון לעומק
if events:
    event = events[0]
    print(f"\n✅ אירוע ראשון: {event.get('title')}")
    print(f"\nכל השדות של האירוע:")
    print(json.dumps(list(event.keys()), indent=2))
    
    if event.get('markets'):
        market = event['markets'][0]
        print(f"\n📊 שוק ראשון:")
        print(f"   Question: {market.get('question')}")
        print(f"\nכל השדות של השוק:")
        print(json.dumps(list(market.keys()), indent=2))
        
        print(f"\n💰 שדות מחיר:")
        print(f"   outcomePrices: {market.get('outcomePrices')}")
        print(f"   outcomes: {market.get('outcomes')}")
        print(f"   clobTokenIds: {market.get('clobTokenIds')}")
        
        # בוא נבדוק אם יש API אחר למחירים
        if market.get('clobTokenIds'):
            token_id = market['clobTokenIds'][0]
            print(f"\n🔍 מושך מחיר מ-CLOB API עבור token: {token_id}")
            
            try:
                price_url = f"https://clob.polymarket.com/prices?token_id={token_id}"
                price_response = requests.get(price_url, timeout=5)
                price_data = price_response.json()
                print(f"   📈 מחיר מ-CLOB: {json.dumps(price_data, indent=2)}")
            except Exception as e:
                print(f"   ❌ שגיאה: {e}")
