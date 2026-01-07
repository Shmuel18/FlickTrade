# debug_why_rejected.py
"""בודק למה שווקים נדחים"""
import sys
sys.path.insert(0, 'src')

import requests
import json
from datetime import datetime, timezone, timedelta

print("🔍 בודק למה שווקים נדחים...")
print("=" * 70)

url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"
response = requests.get(url)
events = response.json()

print(f"✓ קיבלתי {len(events)} אירועים\n")

now = datetime.now(timezone.utc)
min_close_time = now + timedelta(hours=8)

total_markets = 0
crypto_events = 0
non_crypto_events = 0
too_soon_events = 0
inactive_markets = 0
no_tokens = 0
checked_tokens = 0
no_order_book = 0
price_too_high = 0
found_opportunities = 0

for event in events:
    # Check crypto
    tags = event.get("tags", [])
    tag_names = []
    for tag in tags:
        if isinstance(tag, dict):
            value = tag.get("name") or tag.get("slug") or ""
            tag_names.append(value.lower())
        else:
            tag_names.append(str(tag).lower())
    
    title_text = f"{event.get('title', '')} {event.get('description', '')}".lower()
    
    has_crypto_tag = any(keyword in tag for tag in tag_names for keyword in ("crypto", "btc", "bitcoin", "eth", "ethereum"))
    has_crypto_text = any(keyword in title_text for keyword in ("crypto", "bitcoin", "btc", "ethereum", "eth"))
    
    is_crypto = has_crypto_tag or has_crypto_text
    
    if not is_crypto:
        non_crypto_events += 1
        continue
    
    crypto_events += 1
    
    # Check time
    end_date_str = event.get("endDate")
    if not end_date_str:
        continue
    
    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    
    if end_date < min_close_time:
        too_soon_events += 1
        continue
    
    hours_until_close = (end_date - now).total_seconds() / 3600
    
    # Check markets
    markets = event.get("markets", [])
    for market in markets:
        total_markets += 1
        
        if not market.get("active", False) or market.get("closed", False):
            inactive_markets += 1
            continue
        
        # Get tokens
        token_ids = market.get("clobTokenIds", [])
        if isinstance(token_ids, str):
            try:
                token_ids = json.loads(token_ids)
            except:
                token_ids = []
        
        outcomes = market.get("outcomes", [])
        
        if not token_ids or not outcomes:
            no_tokens += 1
            continue
        
        # Check each token
        for idx, token_id in enumerate(token_ids):
            checked_tokens += 1
            outcome_name = outcomes[idx] if idx < len(outcomes) else "Unknown"
            
            # Get price from Order Book
            try:
                book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
                book_response = requests.get(book_url, timeout=2)
                
                if book_response.status_code != 200:
                    no_order_book += 1
                    continue
                
                book = book_response.json()
                bids = book.get("bids", [])
                asks = book.get("asks", [])
                
                if not bids or not asks:
                    no_order_book += 1
                    continue
                
                best_bid = float(bids[0].get("price", 0))
                best_ask = float(asks[0].get("price", 0))
                
                # Check if price is low enough
                if best_ask <= 0.02:
                    found_opportunities += 1
                    print(f"✅ FOUND!")
                    print(f"   Event: {event.get('title', 'Unknown')[:50]}")
                    print(f"   Market: {market.get('question', 'Unknown')[:50]}")
                    print(f"   Outcome: {outcome_name}")
                    print(f"   Price: ${best_ask:.4f} (bid: ${best_bid:.4f})")
                    print(f"   Hours until close: {hours_until_close:.1f}h")
                    print()
                else:
                    price_too_high += 1
                    
            except Exception as e:
                no_order_book += 1
                continue

print("\n" + "=" * 70)
print("סיכום:")
print("=" * 70)
print(f"סה\"כ אירועים: {len(events)}")
print(f"אירועים לא-קריפטו (נדחו): {non_crypto_events}")
print(f"אירועי קריפטו (עברו): {crypto_events}")
print(f"אירועים שנסגרים בפחות מ-8 שעות (נדחו): {too_soon_events}")
print(f"סה\"כ שווקים באירועים שעברו: {total_markets}")
print(f"שווקים לא פעילים/סגורים (נדחו): {inactive_markets}")
print(f"שווקים ללא tokens (נדחו): {no_tokens}")
print(f"סה\"כ tokens שנבדקו: {checked_tokens}")
print(f"Tokens ללא Order Book (נדחו): {no_order_book}")
print(f"Tokens עם מחיר גבוה מדי >0.02 (נדחו): {price_too_high}")
print(f"\n🎯 הזדמנויות שנמצאו: {found_opportunities}")
print("=" * 70)
