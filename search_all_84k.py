"""מחפש אירועי 84k בכל העמודים"""
import requests
from time import sleep

print("🔍 מחפש אירועים עם 84k בכל העמודים...")

all_events = []
offset = 0
limit = 500

while True:
    url = f"https://gamma-api.polymarket.com/events?limit={limit}&offset={offset}"
    print(f"\nמושך עמוד: offset={offset}")
    
    try:
        response = requests.get(url, timeout=15)
        events = response.json()
        
        if not events or len(events) == 0:
            print(f"  ✓ אין עוד אירועים (קיבלתי {len(events)})")
            break
            
        all_events.extend(events)
        print(f"  ✓ קיבלתי {len(events)} אירועים (סה\"כ עד כה: {len(all_events)})")
        
        # חיפוש בעמוד הנוכחי
        events_with_84 = [e for e in events if "84" in e.get("title", "").lower()]
        if events_with_84:
            print(f"\n  🎯 מצאתי אירועים עם '84' בעמוד הזה:")
            for e in events_with_84:
                print(f"    • {e.get('title')}")
                print(f"      Active: {e.get('active')}, Closed: {e.get('closed')}")
        
        if len(events) < limit:
            print(f"\n  ✓ קיבלתי פחות מהלימיט - זה העמוד האחרון")
            break
            
        offset += limit
        
        # בדיקה - אל תמשיך יותר מ-3000
        if offset >= 3000:
            print(f"\n  ⚠️ הגעתי ל-3000 אירועים, עוצר")
            break
            
        sleep(0.5)  # כדי לא להציף את ה-API
        
    except Exception as e:
        print(f"  ❌ שגיאה: {e}")
        break

print(f"\n{'='*70}")
print(f"סיכום:")
print(f"  סה\"כ אירועים שנבדקו: {len(all_events)}")

# חיפוש סופי
bitcoin_events = [e for e in all_events if any(kw in e.get("title", "").lower() for kw in ["bitcoin", "btc", "$btc"])]
print(f"  אירועי Bitcoin/BTC: {len(bitcoin_events)}")

events_with_84 = [e for e in all_events if "84" in e.get("title", "").lower()]
print(f"  אירועים עם '84': {len(events_with_84)}")

jan8_events = [e for e in all_events if any(kw in e.get("title", "").lower() for kw in ["jan 8", "january 8", "jan. 8", "1/8", "01/08"])]
print(f"  אירועי January 8: {len(jan8_events)}")

# האירוע המבוקש
target_events = [e for e in all_events if 
                 any(kw in e.get("title", "").lower() for kw in ["bitcoin", "btc"]) and
                 "84" in e.get("title", "").lower() and
                 any(kw in e.get("title", "").lower() for kw in ["jan 8", "january 8", "1/8"])]

if target_events:
    print(f"\n✅ מצאתי {len(target_events)} אירועים תואמים!")
    for e in target_events:
        print(f"\n  📊 {e.get('title')}")
        print(f"     Active: {e.get('active')}, Closed: {e.get('closed')}")
        print(f"     End Date: {e.get('endDate')}")
        print(f"     Markets: {len(e.get('markets', []))}")
else:
    print(f"\n❌ לא מצאתי את האירוע המבוקש")
    print(f"\n💡 אולי הכותרת שונה? הנה כל אירועי Bitcoin:")
    for e in bitcoin_events[:30]:
        print(f"  • {e.get('title')}")

print(f"{'='*70}")
