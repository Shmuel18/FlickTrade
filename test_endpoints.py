"""מחפש את ה-endpoint הנכון"""
import requests

print("="*70)
print("🔍 בודק endpoints שונים")
print("="*70)

# 1. markets רגיל
print("\n1️⃣ /markets (default)")
resp = requests.get("https://gamma-api.polymarket.com/markets?limit=1000", timeout=15)
print(f"   Got: {len(resp.json())} markets")

# 2. markets עם offset
print("\n2️⃣ /markets with offset=500")
resp = requests.get("https://gamma-api.polymarket.com/markets?limit=500&offset=500", timeout=15)
print(f"   Got: {len(resp.json())} markets")

# 3. events endpoint
print("\n3️⃣ /events")
resp = requests.get("https://gamma-api.polymarket.com/events?limit=1000", timeout=15)
events = resp.json()
print(f"   Got: {len(events)} events")

# חפש bitcoin
bitcoin_events = [e for e in events if "bitcoin" in e.get("title", "").lower()]
print(f"   Bitcoin events: {len(bitcoin_events)}")
for e in bitcoin_events[:3]:
    print(f"   • {e.get('title')}")

# 4. חיפוש ישיר לפי tag
print("\n4️⃣ /markets with tag_id (crypto)")
resp = requests.get("https://gamma-api.polymarket.com/markets?tag_id=crypto&limit=500", timeout=15)
print(f"   Got: {len(resp.json())} crypto markets")

# 5. חיפוש לפי event slug
print("\n5️⃣ /events with slug")
resp = requests.get("https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-january-8", timeout=15)
event = resp.json()
print(f"   Got: {len(event)} events")
if event:
    e = event[0]
    print(f"   Title: {e.get('title')}")
    markets = e.get('markets', [])
    print(f"   Markets in event: {len(markets)}")
    for m in markets:
        print(f"   • {m.get('question')}")
        print(f"     Active: {m.get('active')}, Closed: {m.get('closed')}")

print("\n" + "="*70)
print("💡 מסקנה: צריך לחפש דרך events, לא markets!")
print("="*70)
