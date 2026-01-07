# check_link_market.py
"""בודק את השוק מהקישור"""
import requests

# From the URL structure, let's try to extract the market
# The URL pattern is: /event/{event-slug}/{market-slug}

event_slug = "bitcoin-above-on-january-8"
market_slug = "bitcoin-above-84k-on-january-8"

print(f"🔍 מנסה למצוא את השוק דרך slug...")
print(f"Event slug: {event_slug}")
print(f"Market slug: {market_slug}")
print("=" * 70)

# Try Gamma API with slug
urls_to_try = [
    f"https://gamma-api.polymarket.com/events/{event_slug}",
    f"https://gamma-api.polymarket.com/markets/{market_slug}",
    "https://gamma-api.polymarket.com/events?limit=1000",  # Try more events
]

for url in urls_to_try:
    print(f"\n🔍 {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                print(f"✅ Got event/market data!")
                print(f"Title: {data.get('title')}")
                print(f"Active: {data.get('active')}")
                print(f"Closed: {data.get('closed')}")
                
                if 'markets' in data:
                    print(f"Markets: {len(data['markets'])}")
                    for market in data['markets']:
                        q = market.get('question', '')
                        if '84' in q:
                            print(f"  Found 84k market: {q}")
                            print(f"    Active: {market.get('active')}")
                            print(f"    Closed: {market.get('closed')}")
                            print(f"    Prices: {market.get('outcomePrices')}")
                break
            elif isinstance(data, list):
                print(f"Got {len(data)} items")
                # Search for our event
                for item in data[:100]:  # Check first 100
                    title = item.get('title', '').lower()
                    if 'january 8' in title and 'bitcoin' in title:
                        print(f"\n✅ Found it!")
                        print(f"Title: {item.get('title')}")
                        print(f"Active: {item.get('active')}")
                        print(f"Closed: {item.get('closed')}")
                        print(f"End Date: {item.get('endDate')}")
                        
                        if 'markets' in item:
                            print(f"Markets: {len(item['markets'])}")
                            for market in item['markets'][:5]:
                                print(f"  • {market.get('question', 'Unknown')[:50]}")
                        break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
