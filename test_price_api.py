# test_price_api.py
"""בודק API endpoints שונים למחירים"""
import requests
import json

# נסה כמה endpoints שונים
token_id = "93592949212798121127213117304912625505836768562433217537850469496310204567695"
condition_id = "0xcf1c4ad9203c73e22061c0210f075a0df11dab19bb6e0e0cdc3d1b31b4a9e9af"

print("🔍 מנסה endpoints שונים...\n")

# ניסיון 1: prices endpoint
try:
    url1 = f"https://clob.polymarket.com/prices?token_id={token_id}"
    print(f"1️⃣ {url1}")
    r1 = requests.get(url1, timeout=5)
    print(f"   Status: {r1.status_code}")
    if r1.status_code == 200:
        print(f"   Response: {json.dumps(r1.json(), indent=2)[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print()

# ניסיון 2: price endpoint ללא token_id
try:
    url2 = f"https://clob.polymarket.com/price?token_id={token_id}"
    print(f"2️⃣ {url2}")
    r2 = requests.get(url2, timeout=5)
    print(f"   Status: {r2.status_code}")
    if r2.status_code == 200:
        print(f"   Response: {json.dumps(r2.json(), indent=2)[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print()

# ניסיון 3: markets endpoint
try:
    url3 = f"https://clob.polymarket.com/markets/{condition_id}"
    print(f"3️⃣ {url3}")
    r3 = requests.get(url3, timeout=5)
    print(f"   Status: {r3.status_code}")
    if r3.status_code == 200:
        data = r3.json()
        print(f"   Response keys: {list(data.keys())}")
        if 'tokens' in data:
            for token in data['tokens'][:2]:
                print(f"   Token: {token.get('token_id')[:20]}...")
                print(f"   Price: {token.get('price')}")
except Exception as e:
    print(f"   Error: {e}")

print()

# ניסיון 4: order book
try:
    url4 = f"https://clob.polymarket.com/book?token_id={token_id}"
    print(f"4️⃣ {url4}")
    r4 = requests.get(url4, timeout=5)
    print(f"   Status: {r4.status_code}")
    if r4.status_code == 200:
        data = r4.json()
        if 'bids' in data and data['bids']:
            print(f"   Best Bid: {data['bids'][0].get('price')}")
        if 'asks' in data and data['asks']:
            print(f"   Best Ask: {data['asks'][0].get('price')}")
except Exception as e:
    print(f"   Error: {e}")

print()

# ניסיון 5: midpoint
try:
    url5 = f"https://clob.polymarket.com/midpoint?token_id={token_id}"
    print(f"5️⃣ {url5}")
    r5 = requests.get(url5, timeout=5)
    print(f"   Status: {r5.status_code}")
    if r5.status_code == 200:
        print(f"   Response: {r5.json()}")
except Exception as e:
    print(f"   Error: {e}")
