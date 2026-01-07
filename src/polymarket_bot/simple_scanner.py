# simple_scanner.py
"""סורק שווקים בפוליימרקט - מחפש מחירים קיצוניים בשווקי קריפטו"""
import requests
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"

def scan_extreme_price_markets(
    min_hours_until_close: int = 8,
    max_entry_price: float = 0.004,
    exit_multiplier: float = 2.0,
    focus_crypto: bool = True
) -> List[Dict]:
    """
    סורק שווקים עם מחירים נמוכים לקנייה.
    
    Args:
        min_hours_until_close: מינימום שעות עד סגירת השוק
        max_entry_price: מחיר מקסימלי לקנייה (ברירת מחדל: 0.004 = 0.4 סנט)
        exit_multiplier: יעד יציאה כפולת המחיר (ברירת מחדל: 2.0 = כפל 2)
        focus_crypto: להתמקד רק בשווקי קריפטו
    
    Returns:
        רשימת הזדמנויות קנייה
    """
    try:
        url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit=100"
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
        
        markets_checked = 0
        
        for event in events:
            try:
                # פילטר קריפטו
                if focus_crypto:
                    tags = event.get("tags", [])
                    tag_names = []
                    for tag in tags:
                        if isinstance(tag, dict):
                            value = tag.get("name") or tag.get("slug") or ""
                            tag_names.append(value.lower())
                        else:
                            tag_names.append(str(tag).lower())

                    title_text = f"{event.get('title', '')} {event.get('description', '')}".lower()

                    has_crypto_tag = any(keyword in tag for tag in tag_names for keyword in ("crypto", "btc", "bitcoin", "eth", "ethereum"))
                    has_crypto_text = any(keyword in title_text for keyword in ("crypto", "bitcoin", "btc", "ethereum", "eth"))

                    if not (has_crypto_tag or has_crypto_text):
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
                        if not market.get("active", False) or market.get("closed", False):
                            continue

                        # קבל token IDs
                        token_ids = market.get("clobTokenIds", [])

                        # אם זה string, נסה לפרסר כ-JSON
                        if isinstance(token_ids, str):
                            try:
                                token_ids = json.loads(token_ids)
                            except Exception:
                                token_ids = [token_ids] if token_ids else []

                        outcomes = market.get("outcomes", [])

                        if not token_ids or not outcomes:
                            continue
                        
                        outcome_prices = market.get("outcomePrices", []) or []

                        # לכל token, קבל את המחיר האמיתי
                        for idx, token_id in enumerate(token_ids):
                            outcome_name = outcomes[idx] if idx < len(outcomes) else "Unknown"

                            price_data: Optional[Dict[str, float]] = None

                            # נסה קודם כל להשתמש במחיר מה-Gamma API אם הוא נראה אמין
                            gamma_price = None
                            if idx < len(outcome_prices):
                                try:
                                    gamma_price = float(outcome_prices[idx])
                                except (TypeError, ValueError):
                                    gamma_price = None

                            if gamma_price and 0 < gamma_price < 1:
                                # יש מחיר תקין מ-Gamma, השתמש בו!
                                price_data = {"best_bid": gamma_price * 0.99, "best_ask": gamma_price * 1.01}
                            else:
                                # אין מחיר תקין, נסה Order Book (יכול להיות איטי)
                                price_data = get_current_price(token_id)
                                if not price_data:
                                    # גם Order Book לא עזר, דלג על token זה
                                    continue

                            best_bid = price_data.get("best_bid")
                            best_ask = price_data.get("best_ask")

                            # בדיקה פשוטה: האם מחיר הקנייה (ASK) נמוך מספיק?
                            if best_ask is None or best_ask > max_entry_price:
                                continue

                            # יש לנו הזדמנות!
                            entry_price = best_ask
                            target_exit_price = entry_price * exit_multiplier
                            
                            # יש לנו הזדמנות!
                            entry_price = best_ask
                            target_exit_price = entry_price * exit_multiplier
                            
                            opportunity = {
                                "event_title": event.get("title", "Unknown"),
                                "market_question": market.get("question", "Unknown"),
                                "outcome": outcome_name,
                                "entry_price": entry_price,
                                "target_exit_price": target_exit_price,
                                "current_price": entry_price,
                                "best_bid": best_bid,
                                "best_ask": best_ask,
                                "token_id": token_id,
                                "condition_id": market.get("conditionId"),
                                "hours_until_close": round(hours_until_close, 1),
                                "end_date": end_date_str,
                                "tags": event.get("tags", [])
                            }
                            
                            opportunities.append(opportunity)
                            
                            logger.info(
                                f"✅ מצאתי: {opportunity['event_title'][:50]} | "
                                f"{outcome_name} @ ${entry_price:.4f} | "
                                f"יעד: ${target_exit_price:.4f} | "
                                f"{hours_until_close:.1f}h עד סגירה"
                            )
                    
                    except Exception as e:
                        logger.debug(f"שגיאה בעיבוד שוק: {e}")
                        continue
                
                # עדכון מונה
                markets_checked += len(markets)
                if markets_checked % 50 == 0:
                    logger.info(f"📊 נבדקו {markets_checked} שווקים, נמצאו {len(opportunities)} הזדמנויות")
            
            except Exception as e:
                logger.debug(f"שגיאה בעיבוד אירוע: {e}")
                continue
        
        logger.info(f"🎯 סה\"כ נמצאו {len(opportunities)} הזדמנויות (נבדקו {markets_checked} שווקים)")
        return opportunities
    
    except Exception as e:
        logger.error(f"❌ שגיאה בסריקה: {e}")
        return []


def get_current_price(token_id: str) -> Optional[Dict[str, float]]:
    """
    מחזיר את המחיר הנוכחי של token מסוים.
    
    Args:
        token_id: מזהה ה-token
    
    Returns:
        מילון עם המחיר הנמוך/גבוה או None אם נכשל
    """
    try:
        # השתמש ב-order book API
        url = f"https://clob.polymarket.com/book?token_id={token_id}"
        response = requests.get(url, timeout=2)  # Timeout קצר יותר!
        response.raise_for_status()
        data = response.json()
        
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        best_bid = float(bids[0].get("price", 0)) if bids else None
        best_ask = float(asks[0].get("price", 0)) if asks else None

        price_data: Dict[str, float] = {}

        if best_bid and best_bid > 0:
            price_data["best_bid"] = best_bid
        if best_ask and best_ask > 0:
            price_data["best_ask"] = best_ask

        return price_data if price_data else None
    
    except Exception as e:
        logger.warning(f"לא הצלחתי לקבל מחיר עבור {token_id}: {e}")
        return None
