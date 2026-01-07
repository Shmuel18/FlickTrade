# check_imports.py
"""
בדיקה מהירה שכל ה-imports עובדים
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🧪 בודק imports...")
print("=" * 60)

try:
    print("1️⃣ Importing simple_scanner...", end=" ")
    from polymarket_bot.simple_scanner import scan_extreme_price_markets
    print("✅")
    
    print("2️⃣ Importing simple_trader...", end=" ")
    from polymarket_bot.simple_trader import SimpleTrader
    print("✅")
    
    print("3️⃣ Importing simple_bot...", end=" ")
    from polymarket_bot.simple_bot import SimpleCryptoBot
    print("✅")
    
    print("4️⃣ Importing executor...", end=" ")
    from polymarket_bot.executor import OrderExecutor
    print("✅")
    
    print("5️⃣ Importing config...", end=" ")
    from polymarket_bot.config import API_KEY, CHAIN_ID
    print("✅")
    
    print("\n" + "=" * 60)
    print("✅ כל ה-imports עובדים!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ שגיאה: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
