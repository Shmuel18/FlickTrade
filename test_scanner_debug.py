"""Test scanner with detailed debug output"""
import sys
sys.path.insert(0, 'src')

import requests
import json
from datetime import datetime, timezone, timedelta

print("="*70)
print("DEBUG SCANNER - CHECKING BITCOIN MARKETS")
print("="*70)

# Get events
url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"
response = requests.get(url)
events = response.json()

print(f"\n✓ Got {len(events)} events")

# Find Bitcoin events
bitcoin_events = []
for event in events:
    title = event.get('title', '').lower()
    if 'bitcoin' in title or 'btc' in title:
        bitcoin_events.append(event)

print(f"✓ Found {len(bitcoin_events)} Bitcoin events")

# Check each Bitcoin event
for i, event in enumerate(bitcoin_events[:3]):
    print(f"\n{'='*70}")
    print(f"EVENT {i+1}: {event.get('title', 'No title')}")
    print(f"{'='*70}")
    
    # Check end date
    end_date_str = event.get('endDate')
    if end_date_str:
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        hours_left = (end_date - now).total_seconds() / 3600
        print(f"Hours until close: {hours_left:.1f}h")
    
    # Check markets
    markets = event.get('markets', [])
    print(f"Markets: {len(markets)}")
    
    for j, market in enumerate(markets[:3]):
        print(f"\n  MARKET {j+1}: {market.get('question', 'No question')}")
        print(f"  Active: {market.get('active')} | Closed: {market.get('closed')}")
        
        # Check token IDs
        clob_token_ids = market.get('clobTokenIds', [])
        if isinstance(clob_token_ids, str):
            try:
                clob_token_ids = json.loads(clob_token_ids)
            except:
                pass
        
        print(f"  Token IDs: {len(clob_token_ids)}")
        
        # Check outcome prices from Gamma
        outcome_prices = market.get('outcomePrices', [])
        print(f"  Gamma Prices: {outcome_prices}")
        
        # Check outcomes
        outcomes = market.get('outcomes', [])
        print(f"  Outcomes: {outcomes}")
        
        # For each token, check order book
        for k, token_id in enumerate(clob_token_ids[:2]):
            outcome = outcomes[k] if k < len(outcomes) else "Unknown"
            gamma_price_str = outcome_prices[k] if k < len(outcome_prices) else None
            
            print(f"\n    TOKEN {k+1} ({outcome}):")
            print(f"      Gamma price: {gamma_price_str}")
            
            # Try order book
            try:
                book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
                book_response = requests.get(book_url, timeout=5)
                if book_response.status_code == 200:
                    book = book_response.json()
                    bids = book.get('bids', [])
                    asks = book.get('asks', [])
                    
                    if bids and asks:
                        best_bid = float(bids[0].get('price', 0))
                        best_ask = float(asks[0].get('price', 0))
                        print(f"      Order Book - Bid: {best_bid:.4f} | Ask: {best_ask:.4f}")
                        
                        # Check if extreme
                        is_low = best_ask <= 0.10
                        is_high = best_bid >= 0.990
                        
                        if is_low:
                            print(f"      ✓ EXTREME LOW! (ask={best_ask:.4f} <= 0.10)")
                        if is_high:
                            print(f"      ✓ EXTREME HIGH! (bid={best_bid:.4f} >= 0.990)")
                        
                        if not is_low and not is_high:
                            print(f"      ✗ Not extreme (ask={best_ask:.4f}, bid={best_bid:.4f})")
                    else:
                        print(f"      ✗ No bids/asks in order book")
                else:
                    print(f"      ✗ Order book error: {book_response.status_code}")
            except Exception as e:
                print(f"      ✗ Exception: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("If you see 'EXTREME LOW' or 'EXTREME HIGH' above but scanner finds 0,")
print("then there's a bug in the scanner logic.")
print("="*70)
