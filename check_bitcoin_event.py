"""בדיקה ישירה של events API ומחפש את Bitcoin 84k"""
import requests

print("=" * 60)
print("🔍 מחפש את Bitcoin 84k דרך events API")
print("=" * 60)

# מחפש ישירות עם slug
url = "https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-january-8"
response = requests.get(url, timeout=30)
events = response.json()

print(f"\n✅ נמצא {len(events)} event")

if events:
    event = events[0]
    print(f"\n📌 Event: {event.get('title', 'N/A')}")
    
    markets = event.get('markets', [])
    print(f"📊 מספר שווקים באירוע: {len(markets)}")
    
    for m in markets:
        question = m.get('question', 'N/A')
        outcome_prices = m.get('outcomePrices', '[]')
        active = m.get('active', False)
        closed = m.get('closed', True)
        condition_id = m.get('conditionId', 'N/A')
        
        print(f"\n   • {question}")
        print(f"     Active: {active}, Closed: {closed}")
        print(f"     Prices: {outcome_prices}")
        print(f"     ConditionId: {condition_id[:20]}...")
