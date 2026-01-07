"""דיבוג מפורט - למה לא נמצאות הזדמנויות"""
import sys
sys.path.insert(0, 'src')

import requests
from datetime import datetime, timezone, timedelta

threshold = 0.20

print("="*70)
print("🔍 דיבוג ידני - בודק למה לא נמצאות הזדמנויות")
print("="*70)

# מושך שווקים
url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=100"
response = requests.get(url, timeout=15)
markets = response.json()

now = datetime.now(timezone.utc)
min_close_time = now + timedelta(hours=1)

found = 0
checked = 0

for m in markets[:20]:
    # בדיקות בסיסיות
    if not m.get("active") or m.get("closed"):
        continue
    
    end_date_str = m.get("endDate")
    if not end_date_str:
        continue
    
    try:
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        if end_date < min_close_time:
            continue
    except:
        continue
    
    token_ids = m.get("clobTokenIds")
    if not token_ids:
        continue
    
    import json
    if isinstance(token_ids, str):
        token_ids = json.loads(token_ids)
    
    if len(token_ids) < 2:
        continue
    
    # בודק את השוק
    question = m.get("question", "")[:50]
    yes_token = token_ids[0]
    no_token = token_ids[1]
    
    try:
        # YES price
        book_url = f"https://clob.polymarket.com/book?token_id={yes_token}"
        book_resp = requests.get(book_url, timeout=3)
        if book_resp.status_code != 200:
            continue
        
        yes_asks = book_resp.json().get("asks", [])
        if not yes_asks:
            continue
        
        yes_price = float(yes_asks[0].get("price", 0))
        
        # NO price
        no_book_url = f"https://clob.polymarket.com/book?token_id={no_token}"
        no_book_resp = requests.get(no_book_url, timeout=3)
        no_price = 1.0 - yes_price
        
        if no_book_resp.status_code == 200:
            no_asks = no_book_resp.json().get("asks", [])
            if no_asks:
                no_price = float(no_asks[0].get("price", no_price))
        
        checked += 1
        
        print(f"\n{checked}. {question}")
        print(f"   YES: ${yes_price:.4f} | NO: ${no_price:.4f}")
        
        # בדיקה
        yes_match = (0.0001 <= yes_price <= threshold)
        no_match = (0.0001 <= no_price <= threshold)
        
        if yes_match:
            print(f"   ✅ YES מתאים! (≤${threshold})")
            found += 1
        
        if no_match:
            print(f"   ✅ NO מתאים! (≤${threshold})")
            found += 1
        
        if not yes_match and not no_match:
            print(f"   ❌ שניהם לא מתאימים")
        
        if checked >= 10:
            break
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

print(f"\n{'='*70}")
print(f"📊 סיכום: נבדקו {checked} שווקים, נמצאו {found} הזדמנויות")
print("="*70)
