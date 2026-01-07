"""מחפש שווקי 84k דרך markets endpoint"""
import requests

print("🔍 מחפש שווקים (markets) עם 84k...")
print("="*70)

# נסה דרך markets endpoint
url = "https://gamma-api.polymarket.com/markets?limit=1000"
print(f"\n1. מושך שווקים מ-API: {url}")

try:
    response = requests.get(url, timeout=15)
    markets = response.json()
    print(f"   ✓ קיבלתי {len(markets)} שווקים")
    
    # חיפוש 84k
    print("\n2. מחפש שווקים עם '84'...")
    markets_with_84 = [m for m in markets if "84" in m.get("question", "").lower() or "84" in m.get("description", "").lower()]
    
    if markets_with_84:
        print(f"   ✅ מצאתי {len(markets_with_84)} שווקים!")
        for m in markets_with_84:
            print(f"\n   📊 {m.get('question', 'Unknown')}")
            print(f"      Active: {m.get('active')}, Closed: {m.get('closed')}")
            print(f"      Token ID: {m.get('clobTokenIds', 'N/A')}")
            print(f"      End Date: {m.get('endDate')}")
    else:
        print(f"   ❌ אין שווקים עם '84'")
    
    # חיפוש Bitcoin
    print("\n3. מחפש שווקי Bitcoin/BTC...")
    bitcoin_markets = [m for m in markets if any(kw in m.get("question", "").lower() for kw in ["bitcoin", "btc", "$btc"])]
    print(f"   מצאתי {len(bitcoin_markets)} שווקי Bitcoin")
    
    if bitcoin_markets:
        print("\n   דוגמאות:")
        for m in bitcoin_markets[:10]:
            print(f"     • {m.get('question', 'Unknown')}")
    
    # חיפוש January 8
    print("\n4. מחפש שווקים של January 8...")
    jan8_markets = [m for m in markets if any(kw in m.get("question", "").lower() for kw in ["jan 8", "january 8", "1/8/2026", "jan. 8"])]
    print(f"   מצאתי {len(jan8_markets)} שווקים של Jan 8")
    
    if jan8_markets:
        print("\n   שווקים:")
        for m in jan8_markets:
            print(f"     • {m.get('question', 'Unknown')}")
            print(f"       Active: {m.get('active')}, Closed: {m.get('closed')}")
    
    # חיפוש משולב
    print("\n5. חיפוש משולב: Bitcoin + 84 + Jan 8...")
    target_markets = [m for m in markets if 
                      any(kw in m.get("question", "").lower() for kw in ["bitcoin", "btc"]) and
                      "84" in m.get("question", "").lower()]
    
    if target_markets:
        print(f"   ✅✅✅ מצאתי {len(target_markets)} שווקים תואמים!")
        for m in target_markets:
            print(f"\n   🎯 {m.get('question')}")
            print(f"      Token ID: {m.get('clobTokenIds')}")
            print(f"      Active: {m.get('active')}, Closed: {m.get('closed')}")
            print(f"      End Date: {m.get('endDate')}")
    else:
        print(f"   ❌ לא מצאתי שווק מתאים")
        
except Exception as e:
    print(f"   ❌ שגיאה: {e}")

print("\n" + "="*70)
