"""טסט עם יותר בדיקות מחיר"""
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
print("🧪 טסט עם 200 בדיקות מחיר")
print("="*70)

opportunities = scan_extreme_price_markets(
    min_hours_until_close=1,
    low_price_threshold=BUY_PRICE_THRESHOLD,
    focus_crypto=False,
    max_price_checks=200  # יותר בדיקות
)

print(f"\n✅ נמצאו {len(opportunities)} הזדמנויות!")

if opportunities:
    print("\nדוגמאות:")
    for opp in opportunities[:10]:
        note = opp.get('note', '')
        print(f"  • {opp['market_question'][:60]}")
        print(f"    {opp['outcome']} @ ${opp['current_price']:.4f} {note}")
else:
    print("\n❌ לא נמצאו הזדמנויות")

print("="*70)
