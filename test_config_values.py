"""טסט לבדיקת Single Source of Truth"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.config import BUY_PRICE_THRESHOLD, SELL_MULTIPLIER

print("="*70)
print("🔍 בדיקת Single Source of Truth")
print("="*70)

print(f"\n📊 ערכים מהקונפיג:")
print(f"   BUY_PRICE_THRESHOLD = ${BUY_PRICE_THRESHOLD}")
print(f"   SELL_MULTIPLIER = {SELL_MULTIPLIER}x")
print(f"   Target Sell Price = ${BUY_PRICE_THRESHOLD * SELL_MULTIPLIER}")

print(f"\n✅ אם הריצה של הבוט תציג את אותם ערכים בדיוק - התיקון הצליח!")
print("="*70)
