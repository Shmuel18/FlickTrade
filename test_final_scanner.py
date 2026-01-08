"""בדיקה סופית של הסורק המעודכן"""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.polymarket_bot.simple_scanner import scan_extreme_price_markets

print("=" * 70)
print("🚀 בדיקת הסורק המעודכן - עם events API")
print("=" * 70)

opps = scan_extreme_price_markets(
    low_price_threshold=0.05,  # פחות מ-5 סנט
    max_price_checks=500,
    verbose_rejections=False
)

print(f"\n🎉 נמצאו {len(opps)} הזדמנויות!")
print("=" * 70)

# מחלק לפי קטגוריה
bitcoin_opps = [o for o in opps if 'bitcoin' in o.get('question', '').lower() or 'btc' in o.get('question', '').lower()]
other_opps = [o for o in opps if o not in bitcoin_opps]

if bitcoin_opps:
    print(f"\n🔶 Bitcoin ({len(bitcoin_opps)}):")
    for opp in bitcoin_opps[:10]:
        print(f"  • {opp.get('side', '?')} @ ${opp.get('price', 0):.4f}: {opp.get('question', 'N/A')[:50]}...")

print(f"\n📋 אחרים ({len(other_opps)}):")
for opp in other_opps[:15]:
    print(f"  • {opp.get('side', '?')} @ ${opp.get('price', 0):.4f}: {opp.get('question', 'N/A')[:50]}...")
