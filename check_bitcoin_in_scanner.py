"""בודק אם Bitcoin 84k קיים בשווקים שנמשכו"""
import requests
import json

GAMMA_API = "https://gamma-api.polymarket.com"

print("=" * 60)
print("🔍 מחפש את Bitcoin above 84k בשווקים שנמשכו")
print("=" * 60)

all_markets = []
seen_ids = set()

# שלב 1: markets
print("\n📂 שלב 1: מושך /markets...")
resp = requests.get(f"{GAMMA_API}/markets?active=true&closed=false&limit=500", timeout=30)
markets_batch = resp.json()
print(f"   ✅ {len(markets_batch)} שווקים")

for m in markets_batch:
    cid = m.get("conditionId")
    if cid and cid not in seen_ids:
        seen_ids.add(cid)
        all_markets.append(m)

# מחפש bitcoin
bitcoin_in_markets = [m for m in markets_batch if 'bitcoin' in m.get('question', '').lower()]
print(f"   🔶 Bitcoin שווקים ב-/markets: {len(bitcoin_in_markets)}")

# שלב 2: events
print("\n📂 שלב 2: מושך /events...")
resp = requests.get(f"{GAMMA_API}/events?active=true&closed=false&limit=500", timeout=30)
events_batch = resp.json()
print(f"   ✅ {len(events_batch)} events")

new_from_events = 0
bitcoin_in_events = 0

for event in events_batch:
    event_title = event.get('title', '')
    is_bitcoin_event = 'bitcoin' in event_title.lower()
    
    for m in event.get("markets", []):
        cid = m.get("conditionId")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            all_markets.append(m)
            new_from_events += 1
            
            if 'bitcoin' in m.get('question', '').lower():
                bitcoin_in_events += 1

print(f"   📥 {new_from_events} שווקים חדשים מ-events")
print(f"   🔶 Bitcoin שווקים מ-events: {bitcoin_in_events}")

print(f"\n📊 סה\"כ: {len(all_markets)} שווקים ייחודיים")

# מחפש Bitcoin above
print("\n🔎 מחפש 'Bitcoin above' בכל השווקים:")
for m in all_markets:
    q = m.get('question', '')
    if 'bitcoin' in q.lower() and 'above' in q.lower():
        prices = m.get('outcomePrices', [])
        if isinstance(prices, str):
            prices = json.loads(prices)
        yes_p = float(prices[0]) if prices else 0
        no_p = float(prices[1]) if len(prices) > 1 else 0
        
        marker = ""
        if yes_p < 0.05:
            marker = "🎯 YES זול!"
        elif no_p < 0.05:
            marker = "🎯 NO זול!"
        
        print(f"  • {q[:60]}")
        print(f"    YES: ${yes_p:.4f}  |  NO: ${no_p:.4f}  {marker}")
