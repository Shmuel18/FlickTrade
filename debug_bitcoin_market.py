# debug_bitcoin_market.py
"""בודק למה השוק של Bitcoin לא נמצא"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from polymarket_bot.simple_scanner import scan_extreme_price_markets
import requests
from datetime import datetime, timezone

def check_specific_event():
    """בודק את האירוע הספציפי של Bitcoin"""
    url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=1000"
    
    print("🔍 מחפש שווקי Bitcoin...")
    print()
    
    response = requests.get(url, timeout=15)
    events = response.json()
    
    print(f"📊 סה\"כ אירועים: {len(events)}")
    print()
    
    bitcoin_events = []
    for event in events:
        title = event.get("title", "").lower()
        if "bitcoin" in title or "btc" in title:
            bitcoin_events.append(event)
            
            print(f"✅ מצאתי: {event.get('title')}")
            print(f"   Tags: {event.get('tags', [])}")
            print(f"   End Date: {event.get('endDate')}")
            
            # בדיקת זמן
            end_date_str = event.get("endDate")
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                hours_left = (end_date - now).total_seconds() / 3600
                print(f"   ⏰ שעות עד סגירה: {hours_left:.1f}")
                
                if hours_left < 8:
                    print(f"   ❌ פחות מ-8 שעות - לא עובר!")
            
            # בדיקת תגיות קריפטו
            tags = event.get("tags", [])
            has_crypto = any(
                "crypto" in tag.get("label", "").lower() or 
                "crypto" in tag.get("slug", "").lower() or
                "btc" in tag.get("label", "").lower() or 
                "bitcoin" in tag.get("label", "").lower() 
                for tag in tags if isinstance(tag, dict)
            )
            print(f"   🏷️  יש תג קריפטו: {has_crypto}")
            if not has_crypto:
                print(f"   ❌ אין תג קריפטו - לא עובר!")
            
            # בדיקת מחירים
            print(f"\n   📊 שווקים:")
            for market in event.get("markets", []):
                question = market.get("question", "")
                prices = market.get("outcomePrices", [])
                print(f"      • {question}")
                if prices:
                    for i, price in enumerate(prices):
                        try:
                            p = float(price)
                            outcome = "YES" if i == 0 else "NO"
                            
                            # בדיקה אם עובר
                            passes_low = p <= 0.10
                            passes_high = p >= 0.990
                            
                            status = ""
                            if passes_low:
                                status = "✅ עובר (נמוך)"
                            elif passes_high:
                                status = "✅ עובר (גבוה)"
                            else:
                                status = f"❌ לא עובר ({p:.3f})"
                            
                            print(f"        {outcome}: {p:.4f} - {status}")
                        except:
                            pass
            print()
    
    if not bitcoin_events:
        print("❌ לא מצאתי שווקי Bitcoin!")
        print("\n🔍 מחפש כל שוק עם 'crypto' בתגיות...")
        
        crypto_count = 0
        for event in events:
            tags = event.get("tags", [])
            if any("crypto" in tag.get("slug", "").lower() for tag in tags if isinstance(tag, dict)):
                crypto_count += 1
        
        print(f"📊 מצאתי {crypto_count} שווקי קריפטו")
    else:
        print(f"\n✅ מצאתי {len(bitcoin_events)} שווקי Bitcoin")
    
    print("\n" + "="*60)
    print("עכשיו מריץ את הסורק הרגיל (ללא הגבלת זמן)...")
    print("="*60 + "\n")
    
    opportunities = scan_extreme_price_markets(
        min_hours_until_close=0,  # ללא הגבלת זמן!
        low_price_threshold=0.10,
        high_price_threshold=0.990,
        focus_crypto=True
    )
    
    print(f"\n🎯 הסורק מצא {len(opportunities)} הזדמנויות")
    if opportunities:
        for opp in opportunities[:5]:
            print(f"   • {opp['event_title'][:60]}")
            print(f"     {opp['outcome']} @ ${opp['current_price']:.4f}")

if __name__ == "__main__":
    check_specific_event()
