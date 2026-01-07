# simple_scanner.py
import requests
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"

def scan_extreme_price_markets(
    min_hours_until_close: int = 0,
    low_price_threshold: float = 0.01,
    focus_crypto: bool = False,
    max_price_checks: int = 500  # מגביל כמה שווקים לבדוק (למנוע timeouts)
) -> List[Dict]:
    """סורק מהיר של כל השווקים (עם פאג'ינציה) למציאת מחירים נמוכים."""
    try:
        # שליפת כל השווקים הפעילים עם פאג'ינציה
        markets = []
        offset = 0
        limit = 500
        max_markets = 3000  # הגבלה כדי לא לקחת יותר מדי זמן
        
        logger.info(f"🔍 סורק את כל השווקים בפולימרקט (עם פאג'ינציה)...")
        
        while len(markets) < max_markets:
            url = f"{GAMMA_API_URL}/markets?active=true&closed=false&limit={limit}&offset={offset}"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            batch = response.json()
            
            if not batch or len(batch) == 0:
                break
            
            markets.extend(batch)
            logger.info(f"   📥 נמשכו {len(batch)} שווקים (סה\"כ: {len(markets)})")
            
            if len(batch) < limit:
                break
            
            offset += limit
        
        logger.info(f"✅ סה\"כ נמשכו {len(markets)} שווקים")
        
        # סטטיסטיקות לדיבוג
        stats = {
            "markets_total": len(markets),
            "after_active_filter": 0,
            "after_time_filter": 0,
            "after_tradable_filter": 0,
            "price_fetch_success": 0,
            "price_fetch_fail": 0,
            "prices_seen": [],
            "num_below_threshold": 0
        }
        
        opportunities = []
        now = datetime.now(timezone.utc)
        min_close_time = now + timedelta(hours=min_hours_until_close)
        
        # דוגמאות לדיבוג (10 ראשונים)
        debug_samples = []
        
        for m in markets:
            # בדיקת תקינות בסיסית
            if not m.get("active") or m.get("closed"): continue
            stats["after_active_filter"] += 1
            
            # סינון קריפטו אם מבוקש
            question = m.get("question", "").lower()
            if focus_crypto:
                crypto_keywords = ["bitcoin", "btc", "$btc", "ethereum", "eth", "$eth", 
                                 "crypto", "cryptocurrency", "sol", "solana"]
                if not any(kw in question for kw in crypto_keywords):
                    continue
            
            # בדיקת זמן סגירה
            end_date_str = m.get("endDate")
            if not end_date_str: continue
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                hours_until_close = (end_date - now).total_seconds() / 3600
                if end_date < min_close_time: continue
                stats["after_time_filter"] += 1
            except: continue

            # בדיקת tokens
            token_ids = m.get("clobTokenIds")
            if not token_ids: continue
            
            import json
            if isinstance(token_ids, str):
                try:
                    token_ids = json.loads(token_ids)
                except:
                    continue
            
            if not token_ids or len(token_ids) < 2: continue
            stats["after_tradable_filter"] += 1
            
            # הגבלת מספר בדיקות מחיר כדי לא להיתקע
            if stats["price_fetch_success"] >= max_price_checks:
                break
            
            # כאן הבעיה: outcomePrices זה לא best_ask!
            # זה last price או mid price - לא מה שאנחנו באמת יכולים לקנות בו
            outcome_prices_gamma = m.get("outcomePrices", [])
            
            # מושך מחיר רק פעם אחת - של YES (index 0)
            # ומשם מחשבים את NO
            try:
                yes_token_id = token_ids[0]
                no_token_id = token_ids[1] if len(token_ids) > 1 else None
                
                # קריאה ל-CLOB לקבלת best_ask של YES
                book_url = f"https://clob.polymarket.com/book?token_id={yes_token_id}"
                book_response = requests.get(book_url, timeout=3)
                
                if book_response.status_code != 200:
                    stats["price_fetch_fail"] += 1
                    continue
                
                book = book_response.json()
                asks = book.get("asks", [])
                
                if not asks or len(asks) == 0:
                    stats["price_fetch_fail"] += 1
                    continue
                
                # best_ask של YES
                yes_price = float(asks[0].get("price", 0))
                
                if yes_price <= 0:
                    stats["price_fetch_fail"] += 1
                    continue
                
                # המחיר של NO הוא ההפך (במקרה אידיאלי)
                # אבל בפועל צריך למשוך גם את order book של NO
                # כי יכול להיות spread
                no_price = 1.0 - yes_price  # זה מחיר משוער
                
                if no_token_id:
                    try:
                        no_book_url = f"https://clob.polymarket.com/book?token_id={no_token_id}"
                        no_book_response = requests.get(no_book_url, timeout=3)
                        if no_book_response.status_code == 200:
                            no_book = no_book_response.json()
                            no_asks = no_book.get("asks", [])
                            if no_asks and len(no_asks) > 0:
                                no_price = float(no_asks[0].get("price", no_price))
                    except:
                        pass  # נשאר עם המחיר המשוער
                
                stats["price_fetch_success"] += 1
                stats["prices_seen"].append(yes_price)
                stats["prices_seen"].append(no_price)
                
                # שמירת דוגמה לדיבוג
                if len(debug_samples) < 10:
                    gamma_yes = float(outcome_prices_gamma[0]) if len(outcome_prices_gamma) > 0 else None
                    gamma_no = float(outcome_prices_gamma[1]) if len(outcome_prices_gamma) > 1 else None
                    debug_samples.append({
                        "title": m.get("question", "")[:60],
                        "outcome": f"YES@${yes_price:.4f} / NO@${no_price:.4f}",
                        "gamma_price": gamma_yes,
                        "best_ask": yes_price,
                        "opposite_price": no_price,
                        "hours_until_close": round(hours_until_close, 1)
                    })
                
                # בדיקה 1: YES מתחת ל-threshold
                if 0.0001 <= yes_price <= low_price_threshold:
                    stats["num_below_threshold"] += 1
                    opportunities.append({
                        "event_title": m.get("question", "Unknown"),
                        "market_question": m.get("question", "Unknown"),
                        "outcome": "YES",
                        "current_price": yes_price,
                        "token_id": yes_token_id,
                        "hours_until_close": round(hours_until_close, 1)
                    })
                
                # בדיקה 2: NO מתחת ל-threshold
                if no_token_id and 0.0001 <= no_price <= low_price_threshold:
                    stats["num_below_threshold"] += 1
                    opportunities.append({
                        "event_title": m.get("question", "Unknown"),
                        "market_question": m.get("question", "Unknown"),
                        "outcome": "NO",
                        "current_price": no_price,
                        "token_id": no_token_id,
                        "hours_until_close": round(hours_until_close, 1)
                    })
                    
            except Exception as e:
                stats["price_fetch_fail"] += 1
                continue
        
        # הדפסת סטטיסטיקות מפורטות
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 סטטיסטיקות סריקה:")
        logger.info(f"   Markets total: {stats['markets_total']}")
        logger.info(f"   ├─ After active filter: {stats['after_active_filter']}")
        logger.info(f"   ├─ After time filter: {stats['after_time_filter']}")
        logger.info(f"   └─ After tradable filter: {stats['after_tradable_filter']}")
        logger.info(f"   Price fetches: ✅ {stats['price_fetch_success']} | ❌ {stats['price_fetch_fail']}")
        
        if stats["prices_seen"]:
            import statistics
            prices = sorted(stats["prices_seen"])
            logger.info(f"   Prices distribution:")
            logger.info(f"   ├─ Min: ${min(prices):.4f}")
            logger.info(f"   ├─ P10: ${prices[len(prices)//10]:.4f}")
            logger.info(f"   ├─ Median: ${statistics.median(prices):.4f}")
            logger.info(f"   ├─ P90: ${prices[len(prices)*9//10]:.4f}")
            logger.info(f"   └─ Max: ${max(prices):.4f}")
        
        logger.info(f"   Below threshold (${low_price_threshold}): {stats['num_below_threshold']}")
        logger.info(f"{'='*70}\n")
        
        # הדפסת דוגמאות - תמיד!
        if debug_samples:
            logger.info(f"🔬 דוגמאות מחירים ({len(debug_samples)} שווקים):")
            for sample in debug_samples:
                gamma = sample['gamma_price'] if sample['gamma_price'] else 0
                logger.info(f"   • {sample['title']}")
                logger.info(f"     {sample['outcome']} | Gamma: ${gamma:.4f} | {sample['hours_until_close']}h")
            logger.info("")
        else:
            logger.info(f"⚠️ לא נאספו דוגמאות (אולי כל השווקים נדחו בפילטרים)\n")
        
        if opportunities:
            logger.info(f"🎯 נמצאו {len(opportunities)} הזדמנויות במחיר של ${low_price_threshold} ומטה!")
            # מדפיס את כל ההזדמנויות (לא רק 5 ראשונות)
            for opp in opportunities[:20]:  # מגביל ל-20 בלוגים
                logger.info(f"  • {opp['event_title'][:60]} | {opp['outcome']} @ ${opp['current_price']:.4f}")
            if len(opportunities) > 20:
                logger.info(f"  ... ועוד {len(opportunities) - 20} הזדמנויות נוספות")
        else:
            logger.info(f"❌ לא נמצאו הזדמנויות במחיר של ${low_price_threshold} ומטה")
        
        return opportunities
    except Exception as e:
        logger.error(f"❌ שגיאה בסריקה: {e}")
        return []

def search_markets_by_keywords(keywords: List[str], max_results: int = 3000) -> List[Dict]:
    """מחפש שווקים לפי מילות מפתח (חיפוש גמיש)."""
    try:
        markets = []
        offset = 0
        limit = 500
        
        logger.info(f"🔎 מחפש שווקים עם מילות המפתח: {', '.join(keywords)}")
        
        while len(markets) < max_results:
            url = f"{GAMMA_API_URL}/markets?limit={limit}&offset={offset}"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            batch = response.json()
            
            if not batch or len(batch) == 0:
                break
            
            markets.extend(batch)
            
            if len(batch) < limit:
                break
            
            offset += limit
        
        # סינון לפי מילות מפתח
        matching_markets = []
        for m in markets:
            question = m.get("question", "").lower()
            description = m.get("description", "").lower()
            
            # בדיקה אם כל מילות המפתח נמצאות בשאלה או בתיאור
            if all(any(kw.lower() in text for text in [question, description]) for kw in keywords):
                matching_markets.append({
                    "question": m.get("question"),
                    "active": m.get("active"),
                    "closed": m.get("closed"),
                    "end_date": m.get("endDate"),
                    "token_ids": m.get("clobTokenIds"),
                    "outcome_prices": m.get("outcomePrices"),
                    "outcomes": m.get("outcomes", ["YES", "NO"])
                })
        
        logger.info(f"✅ נמצאו {len(matching_markets)} שווקים מתאימים מתוך {len(markets)}")
        return matching_markets
        
    except Exception as e:
        logger.error(f"❌ שגיאה בחיפוש: {e}")
        return []

def get_current_price(token_id: str) -> Optional[float]:
    """מחזיר מחיר ASK מ-Orderbook עבור פוזיציה קיימת."""
    try:
        url = f"https://clob.polymarket.com/prices?token_id={token_id}"
        data = requests.get(url, timeout=5).json()
        if token_id in data:
            price = float(data[token_id].get("ask", 0))
            return price if price > 0 else None
        return None
    except: return None