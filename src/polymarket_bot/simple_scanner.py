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
    max_price_checks: int = 5000,  # הגדלנו ל-5000
    verbose_rejections: bool = True  # לוגים מפורטים למה נפסל
) -> List[Dict]:
    """סורק מהיר של כל השווקים (עם פאג'ינציה) למציאת מחירים נמוכים."""
    try:
        markets = []
        offset = 0
        limit = 500
        max_markets = 1500  # מקסימום שווקים מ-/markets
        
        # שלב 1: מושך markets ישירות
        logger.info(f"🔍 סורק את כל השווקים בפולימרקט...")
        logger.info(f"   📂 שלב 1: מושך markets ישירות...")
        
        while len(markets) < max_markets:
            url = f"{GAMMA_API_URL}/markets?active=true&closed=false&limit={limit}&offset={offset}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            batch = response.json()
            
            if not batch or len(batch) == 0:
                break
            
            markets.extend(batch)
            
            if len(batch) < limit:
                break
            
            offset += limit
        
        logger.info(f"   ├─ מ-/markets: {len(markets)} שווקים")
        
        # שלב 2: מושך events ומוציא markets מתוכם
        logger.info(f"   📂 שלב 2: מושך events עם markets מוטמעים...")
        
        events_offset = 0
        events_count = 0
        markets_from_events = 0
        seen_condition_ids = set(m.get("conditionId") for m in markets if m.get("conditionId"))
        
        while events_offset < 3000:  # מקסימום 3000 events (כדי לתפוס את Bitcoin above שנמצא ב-offset 2000+)
            events_url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit={limit}&offset={events_offset}"
            
            try:
                events_response = requests.get(events_url, timeout=30)
                events_response.raise_for_status()
                events_batch = events_response.json()
                
                if not events_batch or len(events_batch) == 0:
                    break
                
                events_count += len(events_batch)
                
                # מוציא markets מתוך events
                for event in events_batch:
                    event_markets = event.get("markets", [])
                    for m in event_markets:
                        # רק אם לא ראינו כבר את השוק הזה
                        condition_id = m.get("conditionId")
                        if condition_id and condition_id not in seen_condition_ids:
                            seen_condition_ids.add(condition_id)
                            markets.append(m)
                            markets_from_events += 1
                
                if len(events_batch) < limit:
                    break
                
                events_offset += limit
                
            except Exception as e:
                logger.debug(f"   ⚠️ שגיאה במשיכת events: {e}")
                break
        
        logger.info(f"   ├─ מ-/events: {markets_from_events} שווקים חדשים (מתוך {events_count} events)")
        logger.info(f"   └─ סה\"כ: {len(markets)} שווקים ייחודיים")
        
        # סטטיסטיקות לדיבוג
        stats = {
            "markets_total": len(markets),
            "after_active_filter": 0,
            "after_time_filter": 0,
            "after_tradable_filter": 0,
            "price_fetch_success": 0,
            "price_fetch_fail": 0,
            "prices_seen": [],
            "num_below_threshold": 0,
            # סיבות פסילה
            "rejected_inactive": 0,
            "rejected_no_keyword": 0,
            "rejected_no_enddate": 0,
            "rejected_closing_soon": 0,
            "rejected_no_tokens": 0,
            "rejected_bad_tokens": 0
        }
        
        opportunities = []
        now = datetime.now(timezone.utc)
        min_close_time = now + timedelta(hours=min_hours_until_close)
        
        # דוגמאות לדיבוג (10 ראשונים)
        debug_samples = []
        
        for m in markets:
            question = m.get("question", "")
            question_lower = question.lower()
            
            # בדיקת תקינות בסיסית
            if not m.get("active") or m.get("closed"):
                stats["rejected_inactive"] += 1
                if verbose_rejections and stats["rejected_inactive"] <= 3:
                    logger.debug(f"   ⏭️ נפסל (לא פעיל/סגור): {question[:50]}")
                continue
            stats["after_active_filter"] += 1
            
            # סינון קריפטו אם מבוקש
            if focus_crypto:
                crypto_keywords = ["bitcoin", "btc", "$btc", "ethereum", "eth", "$eth", 
                                 "crypto", "cryptocurrency", "sol", "solana"]
                if not any(kw in question_lower for kw in crypto_keywords):
                    stats["rejected_no_keyword"] += 1
                    if verbose_rejections and stats["rejected_no_keyword"] <= 3:
                        logger.debug(f"   ⏭️ נפסל (לא קריפטו): {question[:50]}")
                    continue
            
            # בדיקת זמן סגירה
            end_date_str = m.get("endDate")
            if not end_date_str:
                stats["rejected_no_enddate"] += 1
                if verbose_rejections and stats["rejected_no_enddate"] <= 3:
                    logger.debug(f"   ⏭️ נפסל (אין תאריך סגירה): {question[:50]}")
                continue
            
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                hours_until_close = (end_date - now).total_seconds() / 3600
                if end_date < min_close_time:
                    stats["rejected_closing_soon"] += 1
                    if verbose_rejections and stats["rejected_closing_soon"] <= 3:
                        logger.debug(f"   ⏭️ נפסל (נסגר בקרוב - {hours_until_close:.1f}h): {question[:50]}")
                    continue
                stats["after_time_filter"] += 1
            except:
                stats["rejected_no_enddate"] += 1
                continue

            # בדיקת tokens
            token_ids = m.get("clobTokenIds")
            if not token_ids:
                stats["rejected_no_tokens"] += 1
                if verbose_rejections and stats["rejected_no_tokens"] <= 3:
                    logger.debug(f"   ⏭️ נפסל (אין clobTokenIds): {question[:50]}")
                continue
            
            import json
            if isinstance(token_ids, str):
                try:
                    token_ids = json.loads(token_ids)
                except:
                    stats["rejected_bad_tokens"] += 1
                    continue
            
            if not token_ids or len(token_ids) < 2:
                stats["rejected_bad_tokens"] += 1
                if verbose_rejections and stats["rejected_bad_tokens"] <= 3:
                    logger.debug(f"   ⏭️ נפסל (tokens לא תקינים): {question[:50]}")
                continue
            stats["after_tradable_filter"] += 1
            
            # הגבלת מספר בדיקות מחיר - רק אם הגענו ל-max
            if stats["price_fetch_success"] >= max_price_checks:
                logger.info(f"⚠️ הגעתי למקסימום {max_price_checks} בדיקות מחיר, עוצר")
                break
            
            # שלב 1: סינון מהיר לפי outcomePrices (לא קוראים ל-CLOB לכולם)
            outcome_prices_gamma = m.get("outcomePrices", [])
            if isinstance(outcome_prices_gamma, str):
                import json as json_module
                try:
                    outcome_prices_gamma = json_module.loads(outcome_prices_gamma)
                except:
                    outcome_prices_gamma = []
            
            # בודקים אם יש מחיר זול לפי outcomePrices (סינון ראשוני)
            has_cheap_gamma_price = False
            for p in outcome_prices_gamma:
                try:
                    if 0.0001 <= float(p) <= low_price_threshold:
                        has_cheap_gamma_price = True
                        break
                except:
                    pass
            
            if not has_cheap_gamma_price:
                continue  # דילוג - אין טעם לקרוא ל-CLOB
            
            # שלב 2: רק לשווקים עם מחיר זול פוטנציאלי - משתמשים ב-outcomePrices ישירות
            # (כדי לא להאט את הסורק עם קריאות CLOB)
            try:
                yes_token_id = token_ids[0]
                no_token_id = token_ids[1] if len(token_ids) > 1 else None
                
                yes_price = float(outcome_prices_gamma[0]) if len(outcome_prices_gamma) > 0 else 0
                no_price = float(outcome_prices_gamma[1]) if len(outcome_prices_gamma) > 1 else 0
                
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
                        "question": m.get("question", "Unknown"),
                        "side": "YES",
                        "price": yes_price,
                        "token_id": yes_token_id,
                        "hours_until_close": round(hours_until_close, 1),
                        "condition_id": m.get("conditionId")
                    })
                
                # בדיקה 2: NO מתחת ל-threshold
                if no_token_id and 0.0001 <= no_price <= low_price_threshold:
                    stats["num_below_threshold"] += 1
                    opportunities.append({
                        "question": m.get("question", "Unknown"),
                        "side": "NO",
                        "price": no_price,
                        "token_id": no_token_id,
                        "hours_until_close": round(hours_until_close, 1),
                        "condition_id": m.get("conditionId")
                    })
                    
            except Exception as e:
                stats["price_fetch_fail"] += 1
                if verbose_rejections and stats["price_fetch_fail"] <= 3:
                    logger.debug(f"   ⏭️ נפסל (שגיאת מחיר): {question[:40]} - {str(e)[:30]}")
                continue
        
        # הדפסת סטטיסטיקות מפורטות
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 סטטיסטיקות סריקה:")
        logger.info(f"   Markets total: {stats['markets_total']}")
        logger.info(f"   ├─ After active filter: {stats['after_active_filter']}")
        logger.info(f"   ├─ After time filter: {stats['after_time_filter']}")
        logger.info(f"   └─ After tradable filter: {stats['after_tradable_filter']}")
        logger.info(f"   Price fetches: ✅ {stats['price_fetch_success']} | ❌ {stats['price_fetch_fail']}")
        
        # הדפסת סיבות פסילה
        logger.info(f"\n📋 סיבות פסילה:")
        logger.info(f"   ├─ לא פעיל/סגור: {stats['rejected_inactive']}")
        if focus_crypto:
            logger.info(f"   ├─ לא קריפטו: {stats['rejected_no_keyword']}")
        logger.info(f"   ├─ אין תאריך סגירה: {stats['rejected_no_enddate']}")
        logger.info(f"   ├─ נסגר בקרוב: {stats['rejected_closing_soon']}")
        logger.info(f"   ├─ אין tokens: {stats['rejected_no_tokens']}")
        logger.info(f"   └─ tokens לא תקינים: {stats['rejected_bad_tokens']}")
        
        if stats["prices_seen"]:
            import statistics
            prices = sorted(stats["prices_seen"])
            logger.info(f"\n📈 התפלגות מחירים:")
            logger.info(f"   ├─ Min: ${min(prices):.4f}")
            logger.info(f"   ├─ P10: ${prices[len(prices)//10]:.4f}")
            logger.info(f"   ├─ Median: ${statistics.median(prices):.4f}")
            logger.info(f"   ├─ P90: ${prices[len(prices)*9//10]:.4f}")
            logger.info(f"   └─ Max: ${max(prices):.4f}")
        
        logger.info(f"\n🎯 Below threshold (${low_price_threshold}): {stats['num_below_threshold']}")
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
                logger.info(f"  • {opp['question'][:60]} | {opp['side']} @ ${opp['price']:.4f}")
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