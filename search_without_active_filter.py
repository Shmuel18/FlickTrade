# search_without_active_filter.py
"""מחפש את השוק ללא פילטר active"""
import requests

print("🔍 מחפש Bitcoin 84k ללא פילטר active...")
print("="*70)

# Try without active=true filter
urls = [
    "https://gamma-api.polymarket.com/events?closed=false&limit=5000",
    "https://gamma-api.polymarket.com/events?limit=5000",
]

for url in urls:
    print(f"\n📍 מנסה: {url}")
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"   ❌ Status: {response.status_code}")
            continue
        
        events = response.json()
        print(f"   ✓ קיבלתי {len(events)} אירועים")
        
        # Search for our event
        for event in events:
            title = event.get("title", "").lower()
            if "bitcoin" in title and "january 8" in title:
                print(f"\n   🎯 מצאתי!")
                print(f"   Title: {event.get('title')}")
                print(f"   Active: {event.get('active')}")
                print(f"   Closed: {event.get('closed')}")
                print(f"   End Date: {event.get('endDate')}")
                print(f"   Markets: {len(event.get('markets', []))}")
                
                # Show first few markets
                markets = event.get('markets', [])
                print(f"\n   דוגמאות לשווקים:")
                for m in markets[:5]:
                    print(f"     • {m.get('question', 'Unknown')[:60]}")
                
                break
        else:
            print(f"   ❌ לא מצאתי")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("מסקנה: אם לא מצאנו, האירוע לא ב-500 הראשונים של ה-API")
print("="*70)
