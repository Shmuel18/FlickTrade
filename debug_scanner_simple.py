# debug_scanner_simple.py
"""בודק את הסורק בצורה פשוטה"""
import requests
import json

print("🔍 בודק API ישירות...")

# קבל אירועים
url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=10"
response = requests.get(url)
events = response.json()

print(f"Got {len(events)} events")

for event in events[:2]:
    print(f"\nEvent: {event.get('title', 'No title')}")
    markets = event.get('markets', [])
    print(f"Markets: {len(markets)}")
    
    for market in markets[:1]:
        print(f"  Question: {market.get('question', 'No question')}")
        print(f"  Active: {market.get('active')}")
        print(f"  Closed: {market.get('closed')}")
        
        # בדוק clobTokenIds
        clob_token_ids = market.get('clobTokenIds', [])
        print(f"  Raw clobTokenIds: {clob_token_ids} (type: {type(clob_token_ids)})")
        
        # נסה לפרסר
        if isinstance(clob_token_ids, str):
            try:
                parsed = json.loads(clob_token_ids)
                print(f"  Parsed clobTokenIds: {parsed}")
                clob_token_ids = parsed
            except Exception as e:
                print(f"  Parse error: {e}")
        
        if clob_token_ids:
            token_id = clob_token_ids[0]
            print(f"  Testing token: {token_id}")
            
            # בדוק order book
            try:
                book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
                book_response = requests.get(book_url, timeout=5)
                if book_response.status_code == 200:
                    book_data = book_response.json()
                    bids = book_data.get('bids', [])
                    asks = book_data.get('asks', [])
                    print(f"    SUCCESS: {len(bids)} bids, {len(asks)} asks")
                    if bids:
                        print(f"    Best bid: {bids[0].get('price')}")
                    if asks:
                        print(f"    Best ask: {asks[0].get('price')}")
                else:
                    print(f"    ERROR: {book_response.status_code}")
            except Exception as e:
                print(f"    EXCEPTION: {e}")