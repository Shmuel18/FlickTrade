"""בדיקה מה המחיר האמיתי"""
import requests

# שוק לדוגמה
url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1"
response = requests.get(url, timeout=15)
market = response.json()[0]

import json
token_ids = market.get("clobTokenIds")
if isinstance(token_ids, str):
    token_ids = json.loads(token_ids)

yes_token = token_ids[0]
no_token = token_ids[1]

print("="*70)
print(f"שוק: {market.get('question', '')[:60]}")
print("="*70)

# YES order book
print("\n📊 YES Token:")
yes_url = f"https://clob.polymarket.com/book?token_id={yes_token}"
yes_resp = requests.get(yes_url, timeout=5).json()

print(f"  Best Ask (למכור YES): ${float(yes_resp['asks'][0]['price']):.4f}" if yes_resp.get('asks') else "  No asks")
print(f"  Best Bid (לקנות YES): ${float(yes_resp['bids'][0]['price']):.4f}" if yes_resp.get('bids') else "  No bids")

# NO order book
print("\n📊 NO Token:")
no_url = f"https://clob.polymarket.com/book?token_id={no_token}"
no_resp = requests.get(no_url, timeout=5).json()

print(f"  Best Ask (למכור NO): ${float(no_resp['asks'][0]['price']):.4f}" if no_resp.get('asks') else "  No asks")
print(f"  Best Bid (לקנות NO): ${float(no_resp['bids'][0]['price']):.4f}" if no_resp.get('bids') else "  No bids")

print("\n" + "="*70)
print("הסבר:")
print("  אם אני רוצה לקנות YES - אני משלם את ה-Best Ask של YES")
print("  אם אני רוצה לקנות NO - אני משלם את ה-Best Ask של NO")
print("="*70)
