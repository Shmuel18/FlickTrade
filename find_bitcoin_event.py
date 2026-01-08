"""מחפש את Bitcoin above event עם pagination"""
import requests

print("🔍 מחפש את 'Bitcoin above' event...")

offset = 0
limit = 500
found = False

while not found and offset < 3000:
    url = f"https://gamma-api.polymarket.com/events?active=true&closed=false&limit={limit}&offset={offset}"
    r = requests.get(url, timeout=30)
    events = r.json()
    
    if not events:
        print(f"  Offset {offset}: 0 events - סיום")
        break
    
    print(f"  Offset {offset}: {len(events)} events")
    
    btc = [e for e in events if 'bitcoin above' in e.get('title', '').lower()]
    if btc:
        print(f"    ✅ נמצא {len(btc)} 'Bitcoin above' events!")
        for e in btc:
            print(f"       • {e.get('title')}")
        found = True
    
    offset += limit

if not found:
    print("❌ לא נמצא 'Bitcoin above' event ב-active events")
    
# מחפש ישירות עם slug
print("\n🔎 מחפש ישירות עם slug...")
r = requests.get("https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-january-8", timeout=30)
events = r.json()
if events:
    e = events[0]
    print(f"✅ נמצא: {e.get('title')}")
    print(f"   Active: {e.get('active')}")
    print(f"   Closed: {e.get('closed')}")
else:
    print("❌ לא נמצא")
