"""בדיקת הסורק הראשי עם Bitcoin"""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.polymarket_bot.simple_scanner import scan_extreme_price_markets

print("=" * 70)
print("🚀 בדיקת הסורק הראשי")
print("=" * 70)

# הגדרות
THRESHOLD = 0.05  # 5 סנט

opps = scan_extreme_price_markets(
    low_price_threshold=THRESHOLD,
    max_price_checks=5000,  # סורק הרבה יותר
    verbose_rejections=False
)

print(f"\n🎉 נמצאו {len(opps)} הזדמנויות מתחת ל-${THRESHOLD}!")

# מחפש bitcoin
bitcoin_opps = [o for o in opps if 'bitcoin' in o.get('question', '').lower()]
print(f"\n🔶 Bitcoin הזדמנויות ({len(bitcoin_opps)}):")
for opp in bitcoin_opps:
    print(f"  💰 {opp.get('side', '?')} @ ${opp.get('price', 0):.4f}: {opp.get('question', 'N/A')[:55]}...")

print(f"\n📋 דוגמאות נוספות ({min(10, len(opps) - len(bitcoin_opps))}):")
for opp in [o for o in opps if o not in bitcoin_opps][:10]:
    print(f"  • {opp.get('side', '?')} @ ${opp.get('price', 0):.4f}: {opp.get('question', 'N/A')[:50]}...")
