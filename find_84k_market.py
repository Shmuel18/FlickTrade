"""בדיקה ישירה של השוק Bitcoin 84k January 8"""
import requests

print("="*70)
print("🔍 מחפש את השוק: Bitcoin above 84k on January 8")
print("="*70)

# 1. חיפוש ישיר ב-API
print("\n1️⃣ חיפוש ב-events API...")
events_url = "https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-january-8"
try:
    resp = requests.get(events_url, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        events = resp.json()
        print(f"   נמצאו: {len(events)} events")
        for e in events:
            print(f"   • {e.get('title', 'No title')}")
            print(f"     Active: {e.get('active')}, Closed: {e.get('closed')}")
except Exception as ex:
    print(f"   Error: {ex}")

# 2. חיפוש לפי slug מלא
print("\n2️⃣ חיפוש markets לפי slug...")
markets_url = "https://gamma-api.polymarket.com/markets?slug=bitcoin-above-84k-on-january-8"
try:
    resp = requests.get(markets_url, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        markets = resp.json()
        print(f"   נמצאו: {len(markets)} markets")
        for m in markets:
            print(f"\n   📊 {m.get('question', 'No question')}")
            print(f"      Active: {m.get('active')}, Closed: {m.get('closed')}")
            print(f"      End Date: {m.get('endDate')}")
            print(f"      clobTokenIds: {m.get('clobTokenIds', 'None')[:50] if m.get('clobTokenIds') else 'None'}...")
except Exception as ex:
    print(f"   Error: {ex}")

# 3. חיפוש חופשי עם מילת מפתח 84
print("\n3️⃣ חיפוש חופשי - markets עם '84k'...")
search_url = "https://gamma-api.polymarket.com/markets?limit=100"
try:
    resp = requests.get(search_url, timeout=10)
    if resp.status_code == 200:
        all_markets = resp.json()
        found = [m for m in all_markets if "84k" in m.get("question", "").lower() or "84,000" in m.get("question", "")]
        print(f"   נמצאו: {len(found)} markets עם 84k")
        for m in found:
            print(f"\n   📊 {m.get('question')}")
            print(f"      Active: {m.get('active')}, Closed: {m.get('closed')}")
except Exception as ex:
    print(f"   Error: {ex}")

# 4. נסה גם עם closed=true
print("\n4️⃣ חיפוש כולל סגורים...")
closed_url = "https://gamma-api.polymarket.com/markets?closed=true&limit=500"
try:
    resp = requests.get(closed_url, timeout=10)
    if resp.status_code == 200:
        closed_markets = resp.json()
        found = [m for m in closed_markets if "84k" in m.get("question", "").lower() or "84,000" in m.get("question", "")]
        print(f"   נמצאו: {len(found)} markets סגורים עם 84k")
        for m in found[:5]:
            print(f"\n   📊 {m.get('question')}")
            print(f"      Active: {m.get('active')}, Closed: {m.get('closed')}")
            print(f"      End Date: {m.get('endDate')}")
except Exception as ex:
    print(f"   Error: {ex}")

# 5. חיפוש לפי condition_id מה-URL
print("\n5️⃣ בדיקת CLOB API ישירות...")
# ננסה לחפש דרך ה-CLOB
clob_url = "https://clob.polymarket.com/markets"
try:
    resp = requests.get(clob_url, timeout=10)
    print(f"   CLOB markets status: {resp.status_code}")
    if resp.status_code == 200:
        clob_data = resp.json()
        print(f"   Type: {type(clob_data)}")
        if isinstance(clob_data, list):
            print(f"   Count: {len(clob_data)}")
            # חפש 84k
            found = [m for m in clob_data if "84" in str(m)]
            print(f"   Found with 84: {len(found)}")
except Exception as ex:
    print(f"   Error: {ex}")

print("\n" + "="*70)
