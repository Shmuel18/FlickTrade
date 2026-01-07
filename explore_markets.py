# explore_markets.py
"""חוקר את כל השווקים הזמינים ב-PolyMarket"""
import requests
import json

# קבל שווקים בלי פילטרים
url = "https://gamma-api.polymarket.com/markets?limit=100"
print(f"🔍 שולח בקשה לכל השווקים: {url}")

response = requests.get(url)
if response.status_code != 200:
    print(f"❌ שגיאה: {response.status_code}")
    exit()

markets = response.json()
print(f"✅ קיבלתי {len(markets)} שווקים")

# ספור לפי סטטוס
active_count = sum(1 for m in markets if m.get('active') and not m.get('closed'))
closed_count = sum(1 for m in markets if m.get('closed'))
inactive_count = sum(1 for m in markets if not m.get('active'))

print(f"📊 סטטיסטיקה:")
print(f"   פעילים: {active_count}")
print(f"   סגורים: {closed_count}")
print(f"   לא פעילים: {inactive_count}")

# הצג כמה שווקים לדוגמה
print(f"\n📋 דוגמאות לשווקים:")
for i, market in enumerate(markets[:10]):
    question = market.get('question', 'No question')[:60] + "..." if len(market.get('question', '')) > 60 else market.get('question', 'No question')
    active = market.get('active')
    closed = market.get('closed')
    status = "פעיל" if active and not closed else "סגור" if closed else "לא פעיל"

    tokens = market.get('tokens', [])
    outcome_prices = market.get('outcomePrices', [])

    print(f"  {i+1}. [{status}] {question}")
    print(f"     ID: {market.get('id')} | Tokens: {len(tokens)} | Prices: {outcome_prices}")

# חפש שווקים עם מחירים אמיתיים (לא ["0", "1"])
print(f"\n🔍 מחפש שווקים עם מחירים אמיתיים...")
real_price_markets = []
for market in markets:
    prices = market.get('outcomePrices', [])
    if prices and len(prices) >= 2:
        try:
            price1 = float(prices[0])
            price2 = float(prices[1])
            if price1 > 0.001 and price1 < 0.999 and price2 > 0.001 and price2 < 0.999:
                real_price_markets.append(market)
        except (ValueError, TypeError):
            continue

print(f"🎯 מצאתי {len(real_price_markets)} שווקים עם מחירים אמיתיים")

for i, market in enumerate(real_price_markets[:5]):
    print(f"\n📊 שוק {i+1}: {market.get('question')}")
    print(f"   ID: {market.get('id')}")
    print(f"   Prices: {market.get('outcomePrices')}")

    tokens = market.get('tokens', [])
    for token in tokens:
        print(f"     Token ID: {token.get('token_id')} - Outcome: {token.get('outcome')} - Price: {token.get('price')}")
