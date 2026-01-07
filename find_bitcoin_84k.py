# find_bitcoin_84k.py
"""מחפש את השוק של Bitcoin 84k"""
import requests
import json
from datetime import datetime, timezone

print("🔍 מחפש: Bitcoin above 84k on January 8")
print("=" * 70)

url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=500"
response = requests.get(url)
events = response.json()

print(f"בודק {len(events)} אירועים...\n")

found = False
for event in events:
    title = event.get("title", "").lower()
    
    if "bitcoin" in title and "january 8" in title:
        print(f"✅ מצאתי את האירוע!")
        print(f"Title: {event.get('title')}")
        print(f"End Date: {event.get('endDate')}")
        
        end_date_str = event.get("endDate")
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            hours_left = (end_date - now).total_seconds() / 3600
            print(f"Hours until close: {hours_left:.1f}h")
        
        # Check tags
        tags = event.get("tags", [])
        print(f"Tags: {tags}")
        
        # Check markets
        markets = event.get("markets", [])
        print(f"\nמספר שווקים: {len(markets)}")
        
        for market in markets:
            question = market.get("question", "")
            if "84" in question or "84k" in question.lower():
                print(f"\n📊 מצאתי את השוק הספציפי!")
                print(f"Question: {question}")
                print(f"Active: {market.get('active')}")
                print(f"Closed: {market.get('closed')}")
                
                # Get tokens
                token_ids = market.get("clobTokenIds", [])
                if isinstance(token_ids, str):
                    try:
                        token_ids = json.loads(token_ids)
                    except:
                        pass
                
                print(f"Token IDs: {len(token_ids)}")
                
                outcomes = market.get("outcomes", [])
                outcome_prices = market.get("outcomePrices", [])
                
                print(f"Outcomes: {outcomes}")
                print(f"Gamma Prices: {outcome_prices}")
                
                # Check Order Book for each token
                for idx, token_id in enumerate(token_ids):
                    outcome = outcomes[idx] if idx < len(outcomes) else "Unknown"
                    print(f"\n  Token {idx+1} ({outcome}):")
                    print(f"    Token ID: {token_id}")
                    
                    try:
                        book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
                        book_response = requests.get(book_url, timeout=5)
                        
                        if book_response.status_code == 200:
                            book = book_response.json()
                            bids = book.get("bids", [])
                            asks = book.get("asks", [])
                            
                            if bids and asks:
                                best_bid = float(bids[0].get("price", 0))
                                best_ask = float(asks[0].get("price", 0))
                                print(f"    Best Bid: ${best_bid:.4f}")
                                print(f"    Best Ask: ${best_ask:.4f}")
                                
                                if best_ask <= 0.04:
                                    print(f"    ✅ המחיר עומד בקריטריון! (≤ 0.04)")
                                else:
                                    print(f"    ❌ המחיר גבוה מדי (> 0.04)")
                            else:
                                print(f"    ❌ אין bids/asks")
                        else:
                            print(f"    ❌ Order Book error: {book_response.status_code}")
                    except Exception as e:
                        print(f"    ❌ Exception: {e}")
                
                found = True

if not found:
    print("❌ לא מצאתי את השוק!")
    print("\nמחפש שווקים דומים...")
    
    for event in events:
        title = event.get("title", "").lower()
        if "bitcoin" in title:
            print(f"  • {event.get('title')}")

print("\n" + "=" * 70)
