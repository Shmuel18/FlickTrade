# debug_bitcoin_84k_full.py
"""בודק למה השוק של Bitcoin 84k לא נמצא"""
import requests
import json
from datetime import datetime, timezone, timedelta

print("="*70)
print("🔍 מחפש: Bitcoin above 84k on January 8")
print("="*70)

# Get all events - ללא פילטר active/closed בשביל לבדוק אם האירוע קיים בכלל
url = "https://gamma-api.polymarket.com/events?limit=5000"
print(f"\n1. מושך אירועים מ-API (בלי פילטר active/closed): {url}")
response = requests.get(url, timeout=15)
events = response.json()
print(f"   ✓ קיבלתי {len(events)} אירועים (active + closed + paused)")

# Search for the event
print("\n2. מחפש את האירוע...")
found_event = None
for event in events:
    title = event.get("title", "").lower()
    # חיפוש גמיש יותר: BTC/Bitcoin + 84k + Jan 8 בכל פורמט
    has_bitcoin = any(keyword in title for keyword in ["bitcoin", "btc", "$btc"])
    has_84k = any(keyword in title for keyword in ["84k", "84,000", "84000", "$84"])
    has_jan8 = any(keyword in title for keyword in ["jan 8", "january 8", "jan. 8", "1/8", "01/08"])
    
    if has_bitcoin and has_84k and has_jan8:
        found_event = event
        print(f"   ✅ מצאתי! Title: {event.get('title')}")
        break

if not found_event:
    print("   ❌ לא מצאתי את האירוע ב-API!")
    print("\n   דוגמאות לאירועי Bitcoin שנמצאו:")
    bitcoin_events = [e for e in events if any(kw in e.get("title", "").lower() for kw in ["bitcoin", "btc", "$btc"])]
    for e in bitcoin_events[:10]:
        print(f"     • {e.get('title')}")
    print(f"\n   סה\"כ אירועי Bitcoin: {len(bitcoin_events)}")
    
    # הצג גם אירועים עם 84k
    print("\n   אירועים שמכילים '84':")
    events_with_84 = [e for e in events if "84" in e.get("title", "").lower()]
    for e in events_with_84[:20]:
        print(f"     • {e.get('title')}")
    exit()

# Check event details
print("\n3. בודק פרטי האירוע...")
end_date_str = found_event.get("endDate")
print(f"   End Date: {end_date_str}")

if end_date_str:
    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    min_close_time = now + timedelta(hours=1)
    hours_until_close = (end_date - now).total_seconds() / 3600
    print(f"   Hours until close: {hours_until_close:.1f}h")
    print(f"   Min required: 1h")
    
    if end_date < min_close_time:
        print(f"   ❌ נדחה: פחות משעה עד סגירה!")
    else:
        print(f"   ✅ עובר: יותר משעה עד סגירה")

# Check markets
print("\n4. בודק שווקים באירוע...")
markets = found_event.get("markets", [])
print(f"   סה\"כ שווקים: {len(markets)}")

# Find the 84k market
found_market = None
for market in markets:
    question = market.get("question", "")
    if "84" in question or "84k" in question.lower():
        found_market = market
        print(f"   ✅ מצאתי את שוק 84k: {question}")
        break

if not found_market:
    print("   ❌ לא מצאתי שוק עם 84k!")
    print("   שווקים זמינים:")
    for m in markets[:10]:
        print(f"     • {m.get('question', 'Unknown')}")
    exit()

# Check if market is active
print("\n5. בודק אם השוק פעיל...")
active = found_market.get("active", False)
closed = found_market.get("closed", False)
print(f"   Active: {active}")
print(f"   Closed: {closed}")

if not active or closed:
    print(f"   ❌ נדחה: השוק לא פעיל!")
    exit()
else:
    print(f"   ✅ עובר: השוק פעיל")

# Check tokens
print("\n6. בודק tokens...")
token_ids = found_market.get("clobTokenIds", [])
print(f"   Raw clobTokenIds type: {type(token_ids)}")
print(f"   Raw clobTokenIds: {token_ids if isinstance(token_ids, str) else 'list'}")

if isinstance(token_ids, str):
    try:
        token_ids = json.loads(token_ids)
        print(f"   ✓ פרסרתי JSON בהצלחה: {len(token_ids)} tokens")
    except Exception as e:
        print(f"   ❌ שגיאה בפרסור: {e}")
        exit()

outcomes = found_market.get("outcomes", [])
print(f"   Outcomes: {outcomes}")

if not token_ids or not outcomes:
    print(f"   ❌ נדחה: אין tokens או outcomes!")
    exit()

print(f"   ✅ עובר: יש {len(token_ids)} tokens")

# Check each token price
print("\n7. בודק מחירים מ-Order Book...")
for idx, token_id in enumerate(token_ids):
    outcome = outcomes[idx] if idx < len(outcomes) else "Unknown"
    print(f"\n   Token {idx+1} ({outcome}):")
    print(f"     Token ID: {token_id[:30]}...")
    
    try:
        book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
        book_response = requests.get(book_url, timeout=5)
        print(f"     Status: {book_response.status_code}")
        
        if book_response.status_code == 200:
            book = book_response.json()
            bids = book.get("bids", [])
            asks = book.get("asks", [])
            
            if bids and asks:
                best_bid = float(bids[0].get("price", 0))
                best_ask = float(asks[0].get("price", 0))
                print(f"     Best Bid: ${best_bid:.4f}")
                print(f"     Best Ask: ${best_ask:.4f}")
                
                if best_ask <= 0.04:
                    print(f"     ✅✅✅ המחיר עומד בקריטריון! (≤ 0.04)")
                    print(f"\n{'='*70}")
                    print("🎯 המסקנה: השוק SHOULD BE FOUND!")
                    print(f"{'='*70}")
                else:
                    print(f"     ❌ נדחה: המחיר גבוה מדי (> 0.04)")
            else:
                print(f"     ❌ נדחה: אין bids או asks")
        else:
            print(f"     ❌ Order Book error: {book_response.status_code}")
    except Exception as e:
        print(f"     ❌ Exception: {e}")

print("\n" + "="*70)
