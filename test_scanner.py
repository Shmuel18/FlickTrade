#!/usr/bin/env python3
# test_scanner.py - Quick test to see what scanner returns

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from polymarket_bot.scanner import scan_polymarket_for_hierarchical_markets

if __name__ == "__main__":
    print("Testing scanner...")
    markets = scan_polymarket_for_hierarchical_markets()
    if markets:
        print(f"Found {len(markets)} markets")
        # Check first market
        first_market = next(iter(markets.values()))
        print(f"First market keys: {list(first_market.keys())}")
        print(f"clob_token_ids type: {type(first_market.get('clob_token_ids'))}")
        print(f"clob_token_ids value: {first_market.get('clob_token_ids')[:2] if first_market.get('clob_token_ids') else 'None'}")
        print(f"all_token_ids type: {type(first_market.get('all_token_ids'))}")
        if first_market.get('all_token_ids'):
            print(f"all_token_ids[0] type: {type(first_market.get('all_token_ids')[0])}")
            print(f"all_token_ids[0] value: {first_market.get('all_token_ids')[0]}")
    else:
        print("No markets found")