"""בדיקה עם threshold גבוה יותר"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets
import logging

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

print("="*70)
print("🧪 בדיקה עם thresholds שונים")
print("="*70)

for threshold in [0.01, 0.05, 0.10, 0.20, 0.30, 0.50]:
    print(f"\n{'─'*70}")
    print(f"📊 בודק threshold = ${threshold}")
    print(f"{'─'*70}")
    
    opportunities = scan_extreme_price_markets(
        min_hours_until_close=0,
        low_price_threshold=threshold,
        focus_crypto=False,
        max_price_checks=100
    )
    
    print(f"   → נמצאו {len(opportunities)} הזדמנויות\n")
    
    if len(opportunities) > 0:
        print(f"   ✅ יש הזדמנויות ב-${threshold}!")
        break

print("="*70)
