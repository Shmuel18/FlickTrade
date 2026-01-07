"""טסט לסורק המשופר - חיפוש גמיש עם פאג'ינציה"""
import sys
sys.path.insert(0, 'src')

from polymarket_bot.simple_scanner import scan_extreme_price_markets, search_markets_by_keywords
import logging

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

print("="*80)
print("🧪 טסט 1: סריקה רגילה עם פאג'ינציה")
print("="*80)

opportunities = scan_extreme_price_markets(
    min_hours_until_close=1,
    low_price_threshold=0.04,
    focus_crypto=False
)

print(f"\n✅ נמצאו {len(opportunities)} הזדמנויות!")
if opportunities:
    print("\nדוגמאות:")
    for opp in opportunities[:10]:
        print(f"  • {opp['market_question'][:70]}")
        print(f"    {opp['outcome']} @ ${opp['current_price']:.4f} | {opp['hours_until_close']}h עד סגירה")

print("\n" + "="*80)
print("🧪 טסט 2: חיפוש ספציפי - Bitcoin + 84k")
print("="*80)

# חיפוש Bitcoin 84k
bitcoin_markets = search_markets_by_keywords(["bitcoin", "84"])
print(f"\n✅ נמצאו {len(bitcoin_markets)} שווקים")

if bitcoin_markets:
    for m in bitcoin_markets:
        print(f"\n  📊 {m['question']}")
        print(f"     Active: {m['active']}, Closed: {m['closed']}")
        print(f"     Prices: {m['outcome_prices']}")
        print(f"     End: {m['end_date']}")
else:
    print("  ❌ לא נמצאו שווקים עם Bitcoin + 84k")

print("\n" + "="*80)
print("🧪 טסט 3: חיפוש גמיש - BTC או Bitcoin")
print("="*80)

# חיפוש כללי יותר
crypto_markets = search_markets_by_keywords(["btc"])
print(f"\n✅ נמצאו {len(crypto_markets)} שווקים עם BTC")

if crypto_markets:
    for m in crypto_markets[:10]:
        print(f"  • {m['question'][:80]}")

print("\n" + "="*80)
print("🧪 טסט 4: סריקה ממוקדת קריפטו")
print("="*80)

crypto_opportunities = scan_extreme_price_markets(
    min_hours_until_close=1,
    low_price_threshold=0.05,
    focus_crypto=True  # רק קריפטו
)

print(f"\n✅ נמצאו {len(crypto_opportunities)} הזדמנויות קריפטו!")
if crypto_opportunities:
    print("\nדוגמאות:")
    for opp in crypto_opportunities[:5]:
        print(f"  • {opp['market_question'][:70]}")
        print(f"    {opp['outcome']} @ ${opp['current_price']:.4f}")

print("\n" + "="*80)
print("✅ כל הטסטים הסתיימו!")
print("="*80)
