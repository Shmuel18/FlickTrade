# quick_test.py
"""בדיקת חיבור מהירה"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from polymarket_bot.executor import OrderExecutor

async def main():
    print("🔌 מתחבר לארנק...")
    print("=" * 60)
    
    try:
        executor = OrderExecutor()
        print(f"✅ חיבור הצליח!")
        print(f"🔑 כתובת: {executor.client.get_address()}")
        print()
        
        print("💵 בודק יתרה...")
        balance = await executor.get_usdc_balance()
        print(f"💰 יתרה: ${balance:.2f} USDC")
        
        if balance >= 10:
            print("✅ יש מספיק יתרה להתחיל!")
        else:
            print("⚠️ יתרה נמוכה - מומלץ לטעון לפחות $20")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
