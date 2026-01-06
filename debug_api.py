#!/usr/bin/env python3
"""
Debug script to check what markets are available from Polymarket API
"""
import requests
import json
from config import GAMMA_API_URL

def debug_scan():
    url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit=500"
    print(f"[DEBUG] Fetching from: {url}\n")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        events = response.json()
        print(f"[INFO] Received {len(events)} events from API\n")
        
        # Count markets by type
        market_types = {}
        total_markets = 0
        markets_with_threshold = 0
        
        for i, event in enumerate(events[:20]):  # Show first 20 events
            title = event.get('title', 'Unknown')
            markets = event.get('markets', [])
            print(f"\n[Event {i+1}] {title}")
            print(f"  Markets: {len(markets)}")
            
            total_markets += len(markets)
            
            for j, market in enumerate(markets[:3]):  # Show first 3 markets
                question = market.get('question', 'N/A')
                token_id = market.get('clobTokenId', market.get('clobTokenIds', 'N/A'))
                print(f"    Market {j+1}: {question[:60]}...")
                print(f"    Token ID: {token_id}")
                
                # Check for threshold keywords
                if any(word in question.lower() for word in ['above', '>', 'over', 'above']):
                    markets_with_threshold += 1
        
        print(f"\n\n[SUMMARY]")
        print(f"Total events: {len(events)}")
        print(f"Total markets: {total_markets}")
        print(f"Markets with threshold keywords: {markets_with_threshold}")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    debug_scan()
