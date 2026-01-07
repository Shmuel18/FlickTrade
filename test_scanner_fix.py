# test_scanner_fix.py
"""בודק את הסורק המעודכן"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets

print("🔍 בודק סורק מעודכן...")

# קודם בלי פילטר קריפטו
opportunities = scan_extreme_price_markets(focus_crypto=False, min_hours_until_close=1)
print(f"בלי פילטר קריפטו: {len(opportunities)} הזדמנויות")

# עכשיו עם פילטר קריפטו
opportunities_crypto = scan_extreme_price_markets(focus_crypto=True, min_hours_until_close=1)
print(f"עם פילטר קריפטו: {len(opportunities_crypto)} הזדמנויות")

# הצג כמה דוגמאות
for opp in opportunities[:3]:
    print(f"  {opp['outcome']} @ {opp['current_price']:.4f} - {opp['hours_until_close']:.1f}h")

for opp in opportunities_crypto[:3]:
    print(f"  CRYPTO: {opp['outcome']} @ {opp['current_price']:.4f} - {opp['hours_until_close']:.1f}h")