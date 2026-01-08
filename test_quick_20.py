"""טסט מהיר עם 20 בדיקות"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets
from polymarket_bot.config import BUY_PRICE_THRESHOLD
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("🚀 טסט מהיר...")

opportunities = scan_extreme_price_markets(
    min_hours_until_close=1,
    low_price_threshold=BUY_PRICE_THRESHOLD,
    focus_crypto=False,
    max_price_checks=20,
    verbose_rejections=True
)

print(f"\n✅ נמצאו {len(opportunities)} הזדמנויות")
