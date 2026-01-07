# test_simple_bot.py
"""
בדיקה מהירה של הבוט - רק סורק ללא ביצוע עסקאות
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from polymarket_bot.simple_scanner import scan_extreme_price_markets
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    print("🧪 בדיקת הסורק...")
    print("=" * 60)
    print("מחפש שווקי קריפטו עם:")
    print("  ✓ מחיר 0.01-0.10 (או 0.990-0.999)")
    print("  ✓ לפחות 8 שעות עד סגירה")
    print("  ✓ קטגוריית קריפטו")
    print("=" * 60)
    print()
    
    # Try with more relaxed parameters first
    print("🔍 ניסיון 1: סריקה רגילה (קריפטו, 8+ שעות)...")
    opportunities = scan_extreme_price_markets(
        min_hours_until_close=8,
        low_price_threshold=0.10,
        high_price_threshold=0.990,
        focus_crypto=True
    )
    
    if not opportunities:
        print("😴 לא נמצאו. מנסה עם פרמטרים רחבים יותר...")
        print("🔍 ניסיון 2: כל שוק קריפטו (ללא הגבלת זמן)...")
        opportunities = scan_extreme_price_markets(
            min_hours_until_close=0,  # Any time
            low_price_threshold=0.15,  # Up to 15 cents
            high_price_threshold=0.85,  # Down to 85 cents
            focus_crypto=True
        )
    
    print(f"\n{'='*60}")
    print(f"📊 סיכום:")
    print(f"{'='*60}")
    print(f"נמצאו {len(opportunities)} הזדמנויות")
    
    if opportunities:
        print("\n🎯 הזדמנויות מובילות:")
        for i, opp in enumerate(opportunities[:10], 1):  # הצג עד 10
            print(f"\n{i}. {opp['event_title'][:60]}")
            print(f"   שאלה: {opp['market_question'][:60]}")
            print(f"   {opp['outcome']} @ ${opp['current_price']:.4f}")
            print(f"   יעד: ${opp['target_exit_price']:.4f} (x{opp['target_exit_price']/opp['current_price']:.1f})")
            print(f"   {opp['hours_until_close']:.1f} שעות עד סגירה")
            print(f"   תגיות: {', '.join(opp['tags'][:3])}")
    else:
        print("\n💡 טיפ: לא תמיד יש שווקים עם מחירים כל כך קיצוניים.")
        print("   הבוט ימשיך לסרוק אוטומטית כל 5 דקות כשהוא רץ.")
    
    print("\n✅ הבדיקה הסתיימה!")

if __name__ == "__main__":
    main()
