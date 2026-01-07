# search_84k_no_filter.py
"""מחפש את השוק ללא פילטרים"""
import requests
import json

print("🔍 מחפש 'Bitcoin above 84k' ללא פילטרים...")
print("=" * 70)

# Try different endpoints
endpoints = [
    "https://gamma-api.polymarket.com/events?limit=500",
    "https://gamma-api.polymarket.com/events?active=true&limit=500",
    "https://gamma-api.polymarket.com/markets?active=true&limit=500",
]

for endpoint in endpoints:
    print(f"\n🔍 בודק: {endpoint}")
    try:
        response = requests.get(endpoint, timeout=10)
        if response.status_code != 200:
            print(f"  ❌ Status: {response.status_code}")
            continue
        
        data = response.json()
        print(f"  ✓ Got {len(data)} items")
        
        # Search for the market
        for item in data:
            title = item.get("title", "").lower()
            question = item.get("question", "").lower()
            
            if ("bitcoin" in title or "bitcoin" in question) and ("84" in title or "84" in question):
                print(f"\n  ✅ FOUND!")
                print(f"    Title: {item.get('title')}")
                print(f"    Question: {item.get('question', 'N/A')}")
                print(f"    Active: {item.get('active')}")
                print(f"    Closed: {item.get('closed')}")
                print(f"    End Date: {item.get('endDate')}")
                break
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)
