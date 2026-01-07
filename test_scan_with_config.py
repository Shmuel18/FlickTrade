"""טסט מהיר לסריקה עם הערכים החדשים"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets
from polymarket_bot.config import BUY_PRICE_THRESHOLD
import logging

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

print("="*70)
print("🧪 טסט סריקה עם Single Source of Truth")
print("="*70)
print(f"\n📊 מחפש שווקים עם מחיר ≤ ${BUY_PRICE_THRESHOLD}")
print("="*70)

opportunities = scan_extreme_price_markets(
    min_hours_until_close=1,
    low_price_threshold=BUY_PRICE_THRESHOLD,
    focus_crypto=False
)

print(f"\n✅ סיימתי! נמצאו {len(opportunities)} הזדמנויות")

if opportunities:
    print("\nדוגמאות:")
    for opp in opportunities[:5]:
        print(f"  • {opp['market_question'][:60]}")
        print(f"    {opp['outcome']} @ ${opp['current_price']:.4f}")
else:
    print(f"\n⚠️ לא נמצאו הזדמנויות במחיר של ${BUY_PRICE_THRESHOLD} ומטה")
    print("   (זה תקין אם אין שווקים כאלה ברגע זה)")

print("="*70)
