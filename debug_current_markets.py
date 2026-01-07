# debug_current_markets.py
"""בודק שווקים עם מחירים נמוכים מאוד ברגע זה"""
import requests
import json
from datetime import datetime, timezone, timedelta

print("🔍 מחפש שווקים עם מחירים נמוכים...")
print("=" * 70)

url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"
response = requests.get(url)
events = response.json()

print(f"✓ Got {len(events)} events\n")

low_price_markets = []
now = datetime.now(timezone.utc)

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
    
    # Check time
    end_date_str = event.get("endDate")
    if not end_date_str:
        continue
    
    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    hours_until_close = (end_date - now).total_seconds() / 3600
    
    markets = event.get("markets", [])
    for market in markets:
        if not market.get("active", False) or market.get("closed", False):
            continue
        
        # Get prices from Gamma
        outcome_prices = market.get("outcomePrices", []) or []
        outcomes = market.get("outcomes", []) or []
        
        for idx, price_str in enumerate(outcome_prices):
            try:
                price = float(price_str)
                if price <= 0.05:  # מחיר עד 5 סנט
                    outcome = outcomes[idx] if idx < len(outcomes) else "Unknown"
                    
                    low_price_markets.append({
                        "event": event.get("title", "Unknown")[:50],
                        "question": market.get("question", "Unknown")[:50],
                        "outcome": outcome,
                        "price": price,
                        "hours": hours_until_close,
                        "is_crypto": is_crypto
                    })
            except (ValueError, TypeError):
                continue

# Sort by price
low_price_markets.sort(key=lambda x: x["price"])

print(f"🎯 Found {len(low_price_markets)} markets with price ≤ 0.05\n")
print("=" * 70)

# Show all markets under 0.02
print("Markets with price ≤ 0.02 (2 cents):")
print("=" * 70)
count_under_002 = 0
for m in low_price_markets:
    if m["price"] <= 0.02:
        count_under_002 += 1
        crypto_tag = "🔶 CRYPTO" if m["is_crypto"] else "⚪"
        time_tag = "✅" if m["hours"] >= 8 else f"⏰ {m['hours']:.1f}h"
        print(f"{crypto_tag} {time_tag}")
        print(f"  Price: ${m['price']:.4f} ({m['price']*100:.2f}%)")
        print(f"  Event: {m['event']}")
        print(f"  Market: {m['question']}")
        print(f"  Outcome: {m['outcome']}")
        print(f"  Hours until close: {m['hours']:.1f}h")
        print()

if count_under_002 == 0:
    print("❌ No markets found with price ≤ 0.02")
    print("\nMarkets with price ≤ 0.05 (5 cents):")
    print("=" * 70)
    for m in low_price_markets[:10]:
        crypto_tag = "🔶 CRYPTO" if m["is_crypto"] else "⚪"
        time_tag = "✅" if m["hours"] >= 8 else f"⏰ {m['hours']:.1f}h"
        print(f"{crypto_tag} {time_tag} ${m['price']:.4f} - {m['event'][:40]}")

print("\n" + "=" * 70)
print("Legend:")
print("  🔶 = Crypto market")
print("  ⚪ = Non-crypto market")
print("  ✅ = 8+ hours until close")
print("  ⏰ = Less than 8 hours")
print("=" * 70)
