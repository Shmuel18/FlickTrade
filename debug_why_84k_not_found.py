"""בדיקה למה הסורק לא מוצא את 84k"""
import sys
sys.path.insert(0, 'src')

import requests
from datetime import datetime, timezone, timedelta

print("="*70)
print("🔍 למה הסורק לא מצא את Bitcoin 84k?")
print("="*70)

# מושך את השוק הספציפי
url = "https://gamma-api.polymarket.com/markets?slug=bitcoin-above-84k-on-january-8"
resp = requests.get(url, timeout=10)
market = resp.json()[0]

print(f"\n📊 השוק: {market.get('question')}")
print(f"   Active: {market.get('active')}")
print(f"   Closed: {market.get('closed')}")
print(f"   End Date: {market.get('endDate')}")

# בדיקת זמן סגירה
end_date_str = market.get('endDate')
end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
now = datetime.now(timezone.utc)
hours_until_close = (end_date - now).total_seconds() / 3600

print(f"\n⏰ זמן עד סגירה: {hours_until_close:.1f} שעות")

if hours_until_close <= 0:
    print("   ❌ השוק כבר נסגר!")
elif hours_until_close < 1:
    print("   ⚠️ פחות משעה עד סגירה - נפסל!")
else:
    print("   ✅ יותר משעה עד סגירה - צריך לעבור")

# בדיקת tokens
import json
token_ids = market.get('clobTokenIds')
if isinstance(token_ids, str):
    token_ids = json.loads(token_ids)

print(f"\n🎟️ Tokens: {len(token_ids)}")
print(f"   YES: {token_ids[0][:40]}...")
print(f"   NO: {token_ids[1][:40]}...")

# בדיקת מחירים
print("\n💰 מחירים מ-Order Book:")
for idx, token_id in enumerate(token_ids):
    outcome = "YES" if idx == 0 else "NO"
    book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
    book_resp = requests.get(book_url, timeout=5)
    if book_resp.status_code == 200:
        book = book_resp.json()
        asks = book.get("asks", [])
        bids = book.get("bids", [])
        
        best_ask = float(asks[0]["price"]) if asks else None
        best_bid = float(bids[0]["price"]) if bids else None
        
        ask_str = f"${best_ask:.4f}" if best_ask else "N/A"
        bid_str = f"${best_bid:.4f}" if best_bid else "N/A"
        print(f"   {outcome}: Ask={ask_str} | Bid={bid_str}")

# למה לא נמצא בחיפוש הרגיל?
print("\n" + "="*70)
print("❓ למה הסורק לא מצא?")
print("="*70)

# בדיקה האם נמצא ב-active markets
active_url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=3000"
resp = requests.get(active_url, timeout=15)
all_markets = resp.json()

print(f"\n📋 סה\"כ markets פעילים: {len(all_markets)}")

# מחפש את השוק שלנו
target_question = market.get('question').lower()
found_in_list = False
position = -1

for i, m in enumerate(all_markets):
    if target_question in m.get("question", "").lower():
        found_in_list = True
        position = i
        break

if found_in_list:
    print(f"   ✅ נמצא במיקום #{position} ברשימה")
else:
    print(f"   ❌ לא נמצא ברשימת 3000!")
    
    # בדוק אם הוא בכלל שם
    condition_id = market.get("conditionId")
    print(f"\n   מחפש לפי conditionId: {condition_id}")
    
    for i, m in enumerate(all_markets):
        if m.get("conditionId") == condition_id:
            print(f"   ✅ נמצא לפי conditionId במיקום #{i}!")
            print(f"   Question: {m.get('question')}")
            found_in_list = True
            break

if not found_in_list:
    print("\n   🔴 השוק לא מוחזר מ-API בכלל!")
    print("   ייתכן שזה באנדפוינט אחר או יש פילטר")

print("\n" + "="*70)
