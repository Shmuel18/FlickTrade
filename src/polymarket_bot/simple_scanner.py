# simple_scanner.py
"""סורק שווקים בפוליימרקט - מחפש מחירים קיצוניים בשווקי קריפטו"""
import requests
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"

def scan_extreme_price_markets(
    min_hours_until_close: int = 8,
    low_price_threshold: float = 0.10,
    high_price_threshold: float = 0.992,
    focus_crypto: bool = True
) -> List[Dict]:
    """
    סורק שווקים עם מחירים קיצוניים (זול מאוד או יקר מאוד).
    
    Args:
        min_hours_until_close: מינימום שעות עד סגירת השוק
        low_price_threshold: מחיר מקסימלי לפוזיציות "זולות" (0.10 = 10%)
        high_price_threshold: מחיר מינימלי לפוזיציות "יקרות" (0.992 = 99.2%)
        focus_crypto: להתמקד רק בשווקי קריפטו
    
    Returns:
        רשימת שווקים מתאימים
    """
    try:
        url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit=500"
        logger.info(f"🔍 סורק שווקים: {url}")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        events = response.json()
        
        if not isinstance(events, list):
            logger.error(f"תגובה לא תקינה מהAPI: {type(events)}")
            return []
        
        logger.info(f"📊 נמצאו {len(events)} אירועים פעילים")
        
        opportunities = []
        now = datetime.now(timezone.utc)
        min_close_time = now + timedelta(hours=min_hours_until_close)
        
        for event in events:
            try:
                # פילטר קריפטו
                if focus_crypto:
                    tags = event.get("tags", [])
                    if not any("crypto" in tag.lower() or "btc" in tag.lower() or 
                              "eth" in tag.lower() or "bitcoin" in tag.lower() or
                              "ethereum" in tag.lower() for tag in tags):
                        continue
                
                # בדיקת זמן סגירה
                end_date_str = event.get("endDate")
                if not end_date_str:
                    continue
                
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                if end_date < min_close_time:
                    continue
                
                hours_until_close = (end_date - now).total_seconds() / 3600
                
                # עבור כל שוק באירוע
                markets = event.get("markets", [])
                for market in markets:
                    try:
                        # מחיר נוכחי
                        outcome_prices = market.get("outcomePrices", [])
                        if not outcome_prices or len(outcome_prices) < 1:
                            continue
                        
                        # בדרך כלל יש YES/NO - נבדוק את שניהם
                        for idx, price_str in enumerate(outcome_prices):
                            try:
                                price = float(price_str)
                            except (ValueError, TypeError):
                                continue
                            
                            # האם המחיר קיצוני?
                            is_extreme_low = price <= low_price_threshold
                            is_extreme_high = price >= high_price_threshold
                            
                            if not (is_extreme_low or is_extreme_high):
                                continue
                            
                            # מידע נוסף
                            token_ids = market.get("clobTokenIds", [])
                            if not token_ids or len(token_ids) <= idx:
                                continue
                            
                            token_id = token_ids[idx]
                            outcome = "YES" if idx == 0 else "NO"
                            
                            opportunity = {
                                "event_title": event.get("title", "Unknown"),
                                "market_question": market.get("question", "Unknown"),
                                "outcome": outcome,
                                "current_price": price,
                                "token_id": token_id,
                                "condition_id": market.get("conditionId"),
                                "hours_until_close": round(hours_until_close, 1),
                                "end_date": end_date_str,
                                "is_extreme_low": is_extreme_low,
                                "is_extreme_high": is_extreme_high,
                                "target_exit_price": price * 2 if is_extreme_low else price / 2,
                                "tags": event.get("tags", [])
                            }
                            
                            opportunities.append(opportunity)
                            
                            logger.info(
                                f"✅ מצאתי: {opportunity['event_title'][:50]} | "
                                f"{outcome} @ ${price:.4f} | "
                                f"יעד: ${opportunity['target_exit_price']:.4f} | "
                                f"{hours_until_close:.1f}h עד סגירה"
                            )
                    
                    except Exception as e:
                        logger.debug(f"שגיאה בעיבוד שוק: {e}")
                        continue
            
            except Exception as e:
                logger.debug(f"שגיאה בעיבוד אירוע: {e}")
                continue
        
        logger.info(f"🎯 סה\"כ נמצאו {len(opportunities)} הזדמנויות")
        return opportunities
    
    except Exception as e:
        logger.error(f"❌ שגיאה בסריקה: {e}")
        return []


def get_current_price(token_id: str) -> Optional[float]:
    """
    מחזיר את המחיר הנוכחי של token מסוים.
    
    Args:
        token_id: מזהה ה-token
    
    Returns:
        מחיר נוכחי או None אם נכשל
    """
    try:
        url = f"https://clob.polymarket.com/prices?token_id={token_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and token_id in data:
            bid = float(data[token_id].get("bid", 0))
            ask = float(data[token_id].get("ask", 0))
            # ממוצע bid-ask
            if bid > 0 and ask > 0:
                return (bid + ask) / 2
        
        return None
    
    except Exception as e:
        logger.warning(f"לא הצלחתי לקבל מחיר עבור {token_id}: {e}")
        return None
