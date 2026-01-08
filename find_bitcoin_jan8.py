"""מחפש ספציפית את שוקי Bitcoin above X"""
import requests
import json

print("=" * 60)
print("🔍 מחפש שוקי Bitcoin January 8")
print("=" * 60)

GAMMA_API = "https://gamma-api.polymarket.com"

# מחפש את האירוע הספציפי
resp = requests.get(f"{GAMMA_API}/events?slug=bitcoin-above-on-january-8", timeout=30)
events = resp.json()

if events:
    event = events[0]
    print(f"\n✅ נמצא event: {event.get('title')}")
    
    markets = event.get("markets", [])
    print(f"\n📊 {len(markets)} שווקי מחיר:")
    print("-" * 60)
    
    for m in markets:
        question = m.get("question", "")
        outcome_prices = m.get("outcomePrices", [])
        
        if isinstance(outcome_prices, str):
            outcome_prices = json.loads(outcome_prices)
        
        yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0
        no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0
        
        # סימון הזדמנויות זולות
        marker = ""
        if yes_price <= 0.10:
            marker = "🎯 YES זול!"
        elif no_price <= 0.10:
            marker = "🎯 NO זול!"
        
        print(f"  {question}")
        print(f"     YES: ${yes_price:.4f}  |  NO: ${no_price:.4f}  {marker}")
        print()
else:
    print("❌ לא נמצא האירוע")
