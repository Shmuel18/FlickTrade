#!/usr/bin/env python3
"""
Debug script to inspect Polymarket API response
Shows actual market structure to identify hierarchical markets
"""
import requests
import json
import sys
from pathlib import Path

# Add parent package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from polymarket_bot.config import GAMMA_API_URL

def debug_api():
    url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit=100"
    
    print("="*80)
    print("POLYMARKET API DEBUG - MARKET ANALYSIS")
    print("="*80)
    print(f"\nFetching from: {url}\n")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        print(f"[INFO] Received {len(events)} events\n")
        
        # Analyze first event in detail
        if events:
            print("="*80)
            print("FIRST EVENT DETAILED ANALYSIS:")
            print("="*80)
            
            first_event = events[0]
            print(f"\nEvent Title: {first_event.get('title', 'N/A')}")
            print(f"Event ID: {first_event.get('id', 'N/A')}")
            print(f"Event Keys: {list(first_event.keys())}")
            
            markets = first_event.get('markets', [])
            print(f"\nMarkets: {len(markets)}")
            
            if markets:
                print("\n" + "-"*80)
                print("FIRST MARKET STRUCTURE:")
                print("-"*80)
                
                market = markets[0]
                print(f"Market Keys: {list(market.keys())}")
                print(f"\nMarket Data:")
                for key, val in market.items():
                    if isinstance(val, (str, int, float, bool)):
                        print(f"  {key}: {val}")
                    elif isinstance(val, list):
                        print(f"  {key}: [{len(val)} items]")
                    elif isinstance(val, dict):
                        print(f"  {key}: {{dict with {len(val)} keys}}")
                
                # Check for token IDs
                print(f"\n[TOKEN ID ANALYSIS]")
                for key in ['clobTokenId', 'clobTokenIds', 'tokenId', 'id']:
                    if key in market:
                        print(f"  {key}: {market[key]}")
        
        # Count events with multiple markets
        print("\n" + "="*80)
        print("SUMMARY STATISTICS:")
        print("="*80)
        
        multi_market_events = 0
        total_markets = 0
        threshold_markets = 0
        
        for event in events[:50]:  # Check first 50
            markets = event.get('markets', [])
            total_markets += len(markets)
            
            if len(markets) > 1:
                multi_market_events += 1
            
            for market in markets:
                q = market.get('question', '').lower()
                if any(word in q for word in ['above', '>', 'over', 'exceed', 'reach']):
                    threshold_markets += 1
        
        print(f"\nTotal events analyzed: {min(50, len(events))}")
        print(f"Events with 2+ markets: {multi_market_events}")
        print(f"Total markets: {total_markets}")
        print(f"Markets with threshold keywords: {threshold_markets}")
        
        # Show some event titles
        print("\n" + "="*80)
        print("SAMPLE EVENT TITLES:")
        print("="*80)
        for i, event in enumerate(events[:20]):
            title = event.get('title', 'N/A')
            markets_count = len(event.get('markets', []))
            print(f"{i+1}. {title} ({markets_count} markets)")
        
        # Show market questions for first event with 2+ markets
        print("\n" + "="*80)
        print("HIERARCHICAL MARKET EXAMPLE:")
        print("="*80)
        for event in events:
            markets = event.get('markets', [])
            if len(markets) >= 2:
                print(f"\nEvent: {event.get('title', 'N/A')}")
                print(f"Markets: {len(markets)}")
                
                for i, market in enumerate(markets[:5]):
                    q = market.get('question', 'N/A')
                    token = market.get('clobTokenId') or market.get('clobTokenIds')
                    print(f"  {i+1}. {q[:70]}")
                    print(f"     Token: {token}")
                
                break
        
        print("\n" + "="*80)
        print("FULL FIRST EVENT JSON:")
        print("="*80)
        if events:
            print(json.dumps(events[0], indent=2)[:2000])
            print("\n... (truncated)")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api()
