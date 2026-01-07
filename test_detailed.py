"""בדיקה מפורטת עם הדפסת דוגמאות"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets
import logging

# הגדרת לוגים ברמת DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s'
)

print("="*70)
print("🧪 בדיקה מפורטת - נראה דוגמאות של מחירים")
print("="*70)

opportunities = scan_extreme_price_markets(
    min_hours_until_close=0,
    low_price_threshold=0.50,  # נסה 50 סנט
    focus_crypto=False,
    max_price_checks=20  # רק 20 כדי לראות מהר
)

print(f"\n✅ נמצאו {len(opportunities)} הזדמנויות")
print("="*70)
