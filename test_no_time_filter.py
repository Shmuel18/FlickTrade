"""טסט ללא פילטר זמן"""
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
print("🧪 טסט ללא פילטר זמן (0 hours)")
print("="*70)

# סריקה ללא פילטר זמן
opportunities = scan_extreme_price_markets(
    min_hours_until_close=0,  # ללא פילטר זמן
    low_price_threshold=BUY_PRICE_THRESHOLD,
    focus_crypto=False,
    max_price_checks=100
)

print(f"\n✅ נמצאו {len(opportunities)} הזדמנויות!")
print("="*70)
