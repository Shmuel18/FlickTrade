# test_with_010.py
"""בודק כמה הזדמנויות יש עם 0.10"""
import sys
sys.path.insert(0, 'src')

import requests
import json

print("🔍 בודק כמה שווקים יש עם מחיר ≤ 0.10...")
print("="*70)

url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=500"
response = requests.get(url, timeout=15)
markets = response.json()

print(f"✓ קיבלתי {len(markets)} שווקים\n")

found_under_010 = 0
found_under_004 = 0

for market in markets[:100]:  # Check first 100 for speed
    if not market.get("active", False) or market.get("closed", False):
        continue
    
    token_ids = market.get("clobTokenIds", [])
    if isinstance(token_ids, str):
        try:
            token_ids = json.loads(token_ids)
        except:
            continue
    
    if not token_ids:
        continue
    
    for token_id in token_ids[:1]:  # Check first token only
        try:
            book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
            book_response = requests.get(book_url, timeout=3)
            
            if book_response.status_code == 200:
                book = book_response.json()
                asks = book.get("asks", [])
                
                if asks:
                    best_ask = float(asks[0].get("price", 999))
                    
                    if best_ask <= 0.10:
                        found_under_010 += 1
                        if best_ask <= 0.04:
                            found_under_004 += 1
                            print(f"✅ {market.get('question', 'Unknown')[:50]} - ${best_ask:.4f}")
        except:
            continue

print(f"\n{'='*70}")
print(f"תוצאות (מתוך 100 שווקים ראשונים):")
print(f"  שווקים עם מחיר ≤ 0.04: {found_under_004}")
print(f"  שווקים עם מחיר ≤ 0.10: {found_under_010}")
print(f"{'='*70}")
