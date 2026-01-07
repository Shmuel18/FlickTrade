# search_bitcoin_markets.py
"""מחפש שווקי ביטקוין ב-PolyMarket"""
import requests
import json

# נסה חיפוש אחר ביטקוין
search_url = "https://gamma-api.polymarket.com/search?query=bitcoin&active=true"
print(f"🔍 מחפש 'bitcoin' ב-Gamma API: {search_url}")

response = requests.get(search_url)
if response.status_code == 200:
    search_results = response.json()
    print(f"✅ קיבלתי תוצאות חיפוש: {len(search_results)}")

    for i, result in enumerate(search_results[:5]):
        print(f"\n📊 תוצאה {i+1}: {result.get('title', 'No title')}")
        print(f"   סוג: {result.get('type')}")

        if result.get('type') == 'market':
            market_data = result.get('market', {})
            print(f"   שוק ID: {market_data.get('id')}")
            print(f"   פעיל: {market_data.get('active')}")
            print(f"   סגור: {market_data.get('closed')}")

            tokens = market_data.get('tokens', [])
            print(f"   Tokens: {len(tokens)}")

            for token in tokens:
                print(f"     Token ID: {token.get('token_id')} - Outcome: {token.get('outcome')} - Price: {token.get('price')}")

            if 'outcomePrices' in market_data:
                print(f"   Outcome Prices: {market_data['outcomePrices']}")

else:
    print(f"❌ שגיאה בחיפוש: {response.status_code}")

print("\n" + "="*50)

# נסה גם את ה-API הרגיל עם סינון אחר
print("🔍 מנסה API עם סינון אחר...")
url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=50"
print(f"שולח בקשה ל: {url}")

response = requests.get(url)
if response.status_code == 200:
    markets = response.json()
    print(f"✅ קיבלתי {len(markets)} שווקים")

    # חפש שווקי ביטקוין
    bitcoin_markets = []
    for market in markets:
        question = market.get('question', '').lower()
        if 'bitcoin' in question or 'btc' in question:
            bitcoin_markets.append(market)

    print(f"🎯 מצאתי {len(bitcoin_markets)} שווקי ביטקוין")

    for i, market in enumerate(bitcoin_markets[:3]):
        print(f"\n📊 שוק {i+1}: {market.get('question')}")
        print(f"   ID: {market.get('id')}")
        print(f"   פעיל: {market.get('active')}")
        print(f"   סגור: {market.get('closed')}")

        tokens = market.get('tokens', [])
        print(f"   Tokens: {len(tokens)}")

        for token in tokens:
            print(f"     Token ID: {token.get('token_id')} - Outcome: {token.get('outcome')} - Price: {token.get('price')}")

        if 'outcomePrices' in market:
            print(f"   Outcome Prices: {market['outcomePrices']}")

else:
    print(f"❌ שגיאה: {response.status_code}")
