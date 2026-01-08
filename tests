import requests

print("🔍 בודק את המגבלה של Gamma API...")

for limit in [500, 1000, 2000, 5000]:
    try:
        print(f"\nמנסה limit={limit}...")
        url = f"https://gamma-api.polymarket.com/events?active=true&closed=false&limit={limit}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ קיבלתי {len(data)} אירועים")
        else:
            print(f"  ❌ Status: {r.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)
print("המסקנה: ה-API מחזיר מקסימום _____ אירועים")
