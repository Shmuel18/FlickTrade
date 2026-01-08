"""בדיקת הסורק המעודכן - מחפש שוקי Bitcoin ספציפית"""
import requests
import json

print("=" * 60)
print("🔍 מחפש הזדמנויות זולות בפולימרקט")
print("=" * 60)

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# פרמטרים
LOW_THRESHOLD = 0.10  # פחות מ-10 סנט

all_markets = []
seen_ids = set()

# מושך markets ו-events במקביל
print("\n📂 שלב 1: מושך /markets...")
try:
    resp = requests.get(f"{GAMMA_API}/markets?active=true&closed=false&limit=500", timeout=30)
    markets_batch = resp.json()
    print(f"   ✅ {len(markets_batch)} שווקים מ-/markets")
    for m in markets_batch:
        cid = m.get("conditionId")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            all_markets.append(m)
except Exception as e:
    print(f"   ❌ שגיאה: {e}")

print("\n📂 שלב 2: מושך /events...")
try:
    resp = requests.get(f"{GAMMA_API}/events?active=true&closed=false&limit=500", timeout=30)
    events_batch = resp.json()
    print(f"   ✅ {len(events_batch)} events")
    
    new_from_events = 0
    for event in events_batch:
        for m in event.get("markets", []):
            cid = m.get("conditionId")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                all_markets.append(m)
                new_from_events += 1
    print(f"   📥 {new_from_events} שווקים חדשים מ-events")
except Exception as e:
    print(f"   ❌ שגיאה: {e}")

print(f"\n📊 סה\"כ: {len(all_markets)} שווקים ייחודיים")

# מחפש הזדמנויות זולות
print(f"\n🎯 מחפש מחירים מתחת ל-${LOW_THRESHOLD:.2f}...")

opportunities = []
checked = 0
max_checks = 100  # מגביל כדי לא לקחת יותר מדי זמן

for m in all_markets:
    if not m.get("active") or m.get("closed"):
        continue
    
    token_ids = m.get("clobTokenIds")
    if not token_ids:
        continue
    if isinstance(token_ids, str):
        try:
            token_ids = json.loads(token_ids)
        except:
            continue
    if not token_ids or len(token_ids) < 2:
        continue
    
    if checked >= max_checks:
        break
    checked += 1
    
    # בודק מחיר מ-outcomePrices כסינון ראשוני (מהיר)
    outcome_prices = m.get("outcomePrices", [])
    if isinstance(outcome_prices, str):
        try:
            outcome_prices = json.loads(outcome_prices)
        except:
            outcome_prices = []
    
    has_cheap_price = False
    for p in outcome_prices:
        try:
            if float(p) < LOW_THRESHOLD:
                has_cheap_price = True
                break
        except:
            pass
    
    if not has_cheap_price:
        continue
    
    # מצאנו שוק עם מחיר פוטנציאלי זול - מוסיף לרשימה
    yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0
    no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0
    
    cheap_side = "YES" if yes_price < LOW_THRESHOLD else "NO"
    cheap_price = yes_price if yes_price < LOW_THRESHOLD else no_price
    
    opportunities.append({
        "question": m.get("question", "N/A"),
        "side": cheap_side,
        "price": cheap_price,
        "token_id": token_ids[0] if cheap_side == "YES" else token_ids[1],
        "condition_id": m.get("conditionId")
    })

print(f"\n🎉 נמצאו {len(opportunities)} הזדמנויות!")
print("=" * 60)

# מחפש bitcoin
bitcoin_opps = [o for o in opportunities if 'bitcoin' in o['question'].lower() or 'btc' in o['question'].lower()]
print(f"\n🔶 Bitcoin הזדמנויות ({len(bitcoin_opps)}):")
for opp in bitcoin_opps:
    print(f"  💰 {opp['side']} @ ${opp['price']:.4f}: {opp['question'][:55]}...")

print(f"\n📋 אחרים ({len(opportunities) - len(bitcoin_opps)}):")
for opp in [o for o in opportunities if o not in bitcoin_opps][:15]:
    print(f"  💰 {opp['side']} @ ${opp['price']:.4f}: {opp['question'][:55]}...")
