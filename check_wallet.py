#!/usr/bin/env python3
"""
בדיקת יתרה ופוזיציות דרך Polygonscan API
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS', '0x6f01ab96024b7e4b87e60f18773c2566b7c8cc23')
USDC_CONTRACT = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC on Polygon

print("\n" + "="*70)
print("💰 בדיקת ארנק Polymarket")
print("="*70)
print(f"\n📍 כתובת Funder: {FUNDER_ADDRESS}")
print(f"🔗 צפייה בבלוקצ'יין: https://polygonscan.com/address/{FUNDER_ADDRESS}")
print("-"*70)

# Try to get balance from Polygonscan API
print("\n🔍 בודק יתרת USDC...")
try:
    # Polygonscan API (free, no key needed for basic queries)
    url = f"https://api.polygonscan.com/api"
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": USDC_CONTRACT,
        "address": FUNDER_ADDRESS,
        "tag": "latest"
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data.get('status') == '1' and data.get('result'):
        balance_wei = int(data['result'])
        balance_usdc = balance_wei / 1_000_000  # USDC has 6 decimals
        
        print(f"💵 יתרת USDC: ${balance_usdc:.6f}")
        print()
        
        if balance_usdc < 0.01:
            print("❌ הארנק כמעט ריק!")
            print("   📌 פתרון: הפקד USDC דרך https://polymarket.com")
            print("   📌 לחץ על 'Deposit' והעבר USDC מבורסה או ארנק אחר")
        elif balance_usdc < 5:
            print(f"⚠️  יתרה נמוכה (${balance_usdc:.2f})")
            print("   Polymarket דורש מינימום $5 למסחר")
            print("   📌 צריך להפקיד עוד כדי לסחור")
        else:
            print(f"✅ יתרה מספיקה למסחר!")
            print(f"   ניתן לבצע ~{int(balance_usdc/5)} עסקאות של $5 כל אחת")
            print(f"   או עסקאות גדולות יותר (עד ${balance_usdc:.2f})")
    else:
        print("⚠️  לא ניתן לקבל יתרה מה-API")
        print(f"   בדוק ידנית: https://polygonscan.com/address/{FUNDER_ADDRESS}")
        
except Exception as e:
    print(f"⚠️  שגיאה בבדיקה: {e}")
    print(f"   בדוק ידנית: https://polygonscan.com/address/{FUNDER_ADDRESS}")

# Check MATIC balance for gas
print("\n🔍 בודק יתרת MATIC (לגאז)...")
try:
    params = {
        "module": "account",
        "action": "balance",
        "address": FUNDER_ADDRESS,
        "tag": "latest"
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data.get('status') == '1' and data.get('result'):
        matic_wei = int(data['result'])
        matic_balance = matic_wei / 1e18
        
        print(f"⛽ יתרת MATIC: {matic_balance:.6f}")
        
        if matic_balance < 0.01:
            print("⚠️  יתרת MATIC נמוכה - עלול להיות בעיה עם גאז")
            print("   (אבל בדרך כלל Polymarket משתמש בגאז של הפרוקסי)")
        else:
            print("✅ יתרת MATIC מספיקה")
            
except Exception as e:
    print(f"⚠️  לא ניתן לבדוק MATIC: {e}")

print("\n" + "="*70)
print("📚 הסבר:")
print("="*70)
print("""
אם אין יתרה:
  1. לך ל-https://polymarket.com
  2. התחבר עם האימייל שלך
  3. לחץ 'Deposit'
  4. העבר USDC מבורסה (Coinbase, Binance וכו')
  5. או קנה USDC דרך Moonpay/Transak (ישירות באתר)

אם יש יתרה אבל הבוט אומר "not enough balance":
  1. ייתכן שיש לך פוזיציות פתוחות שקושרות את הכסף
  2. בדוק באתר Polymarket.com אם יש לך עסקאות פתוחות
  3. סגור עסקאות ישנות כדי לשחרר כסף
  
אם יש יתרה אבל "not enough allowance":
  1. צריך לאשר ל-Polymarket להשתמש ב-USDC שלך
  2. תבצע עסקה אחת באתר ידנית - זה יאשר אוטומטית
  3. או הרץ approve_allowance.py (אם קיים)
""")
print("="*70 + "\n")
