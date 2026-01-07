"""טסט מהיר עם הדפסות debug"""
import sys
sys.path.insert(0, 'src')

import requests
from datetime import datetime, timezone, timedelta

print("="*70)
print("🔍 בדיקה ידנית של שוק אחד")
print("="*70)

# מושך שוק אחד
url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=5"
response = requests.get(url, timeout=15)
markets = response.json()

print(f"\nמצאתי {len(markets)} שווקים")

threshold = 0.20
opportunities_found = []

for m in markets[:3]:  # רק 3 ראשונים
    question = m.get("question", "")
    print(f"\n{'─'*70}")
    print(f"שוק: {question[:60]}")
    
    token_ids = m.get("clobTokenIds")
    if not token_ids:
        print("  ❌ אין token IDs")
        continue
    
    import json
    if isinstance(token_ids, str):
        token_ids = json.loads(token_ids)
    
    print(f"  Tokens: {len(token_ids)}")
    
    for idx, token_id in enumerate(token_ids[:2]):  # YES ו-NO
        outcome = "YES" if idx == 0 else "NO"
        print(f"\n  🔍 בודק {outcome}...")
        
        try:
            book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
            book_response = requests.get(book_url, timeout=3)
            
            if book_response.status_code != 200:
                print(f"     ❌ Status: {book_response.status_code}")
                continue
            
            book = book_response.json()
            asks = book.get("asks", [])
            
            if not asks:
                print(f"     ❌ אין asks")
                continue
            
            best_ask = float(asks[0].get("price", 0))
            opposite_price = 1.0 - best_ask
            
            print(f"     Best Ask: ${best_ask:.4f}")
            print(f"     Opposite: ${opposite_price:.4f}")
            
            # בדיקה
            if 0.0001 <= best_ask <= threshold:
                print(f"     ✅ MATCH! קונים {outcome} @ ${best_ask:.4f}")
                opportunities_found.append((question, outcome, best_ask))
            
            if 0.0001 <= opposite_price <= threshold:
                opposite_outcome = "NO" if idx == 0 else "YES"
                opposite_idx = 1 - idx
                if opposite_idx < len(token_ids):
                    print(f"     ✅ OPPOSITE MATCH! קונים {opposite_outcome} @ ${opposite_price:.4f}")
                    opportunities_found.append((question, opposite_outcome, opposite_price))
        
        except Exception as e:
            print(f"     ❌ Error: {e}")

print(f"\n{'='*70}")
print(f"📊 סיכום: נמצאו {len(opportunities_found)} הזדמנויות")
for q, o, p in opportunities_found:
    print(f"  • {q[:50]} | {o} @ ${p:.4f}")
print("="*70)
