# find_active_markets.py
"""מוצא שווקים פעילים ב-PolyMarket"""
import requests
import json

# נסה endpoints שונים
endpoints = [
    "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=200",
    "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=200",
    "https://gamma-api.polymarket.com/events?limit=200",
    "https://gamma-api.polymarket.com/markets?limit=200"
]

for url in endpoints:
    print(f"\n🔍 בודק: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ קיבלתי {len(data)} פריטים")

            # ספור שווקים פעילים
            active_markets = []
            for item in data:
                markets = item.get('markets', []) if 'markets' in item else [item] if 'question' in item else []
                for market in markets:
                    if market.get('active') and not market.get('closed'):
                        active_markets.append(market)

            print(f"🎯 שווקים פעילים: {len(active_markets)}")

            if active_markets:
                # הצג כמה דוגמאות
                for i, market in enumerate(active_markets[:3]):
                    question = market.get('question', 'No question')[:50] + "..."
                    prices = market.get('outcomePrices', [])
                    print(f"   {i+1}. {question} | Prices: {prices}")

                    tokens = market.get('tokens', [])
                    if tokens:
                        for token in tokens[:2]:  # הצג 2 tokens ראשונים
                            print(f"      Token: {token.get('token_id')[:20]}... - Price: {token.get('price')}")

                # עצור אחרי שמוצאים שווקים פעילים
                break
        else:
            print(f"❌ שגיאה: {response.status_code}")

    except Exception as e:
        print(f"❌ שגיאה: {e}")

# אם לא מצאנו שווקים פעילים, בוא ננסה endpoint אחר
if not active_markets:
    print(f"\n🔄 לא מצאנו שווקים פעילים, מנסה endpoint אחר...")

    # נסה את ה-API הישן יותר
    try:
        url = "https://api.polymarket.com/markets"
        print(f"🔍 בודק API ישן: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ קיבלתי {len(data)} שווקים מה-API הישן")

            active_count = sum(1 for m in data if m.get('active') and not m.get('closed'))
            print(f"🎯 שווקים פעילים: {active_count}")

            if active_count > 0:
                for i, market in enumerate(data[:5]):
                    if market.get('active') and not market.get('closed'):
                        question = market.get('question', 'No question')[:50] + "..."
                        prices = market.get('outcomePrices', [])
                        print(f"   {i+1}. {question} | Prices: {prices}")
        else:
            print(f"❌ שגיאה: {response.status_code}")
    except Exception as e:
        print(f"❌ שגיאה: {e}")
