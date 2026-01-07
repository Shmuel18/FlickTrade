"""טסט סופי - בדיקה מהירה"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets
from polymarket_bot.config import BUY_PRICE_THRESHOLD
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("="*70)
print("🚀 טסט סופי - האם הכל עובד?")
print("="*70)

# סריקה מהירה
opportunities = scan_extreme_price_markets(
    min_hours_until_close=1,
    low_price_threshold=BUY_PRICE_THRESHOLD,
    focus_crypto=False,
    max_price_checks=30  # רק 30 כדי שיהיה מהר
)

print(f"\n{'='*70}")
if opportunities:
    print(f"✅ מצוין! נמצאו {len(opportunities)} הזדמנויות!")
    print(f"\nדוגמאות:")
    for opp in opportunities[:5]:
        print(f"  • {opp['market_question'][:55]}")
        print(f"    {opp['outcome']} @ ${opp['current_price']:.4f}")
    print(f"\n🎯 הבוט עובד מצוין!")
else:
    print(f"⚠️ לא נמצאו הזדמנויות (threshold=${BUY_PRICE_THRESHOLD})")
    print(f"   זה יכול להיות תקין אם אין שווקים זולים ברגע זה")

print("="*70)
