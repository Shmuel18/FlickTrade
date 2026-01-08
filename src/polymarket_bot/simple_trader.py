# simple_trader.py
import logging
from typing import Dict, Optional
from .executor import OrderExecutor
from .config import SELL_MULTIPLIER

logger = logging.getLogger(__name__)

class SimpleTrader:
    def __init__(self, executor: OrderExecutor, position_size_usd: float = 10.0):
        self.executor = executor
        self.position_size_usd = position_size_usd
        self.open_positions: Dict[str, Dict] = {}
        self.target_multiplier = SELL_MULTIPLIER  # מהקונפיג 

    async def check_entry(self, opportunity: Dict) -> bool:
        token_id = opportunity["token_id"]
        if token_id in self.open_positions: return False
        
        price = opportunity.get("price") or opportunity.get("current_price", 0)
        
        # הגנה קריטית נגד חלוקה באפס (WinError/ZeroDivision)
        if price <= 0:
            price = 0.001 
        
        # חישוב יחידות (פולימרקט דורשים מינימום 5 יחידות בדר"כ)
        shares = int(self.position_size_usd / price)
        if shares < 5: return False
        
        question = opportunity.get('question') or opportunity.get('event_title', 'Unknown')
        side = opportunity.get('side') or opportunity.get('outcome', '?')
        logger.info(f"🎯 קונה {shares} יחידות של {side} ב-שוק: {question[:40]}...")
        
        # ביצוע הקנייה
        order_result = self.executor.execute_trade(
            token_id=token_id, side="BUY", size=shares, price=price
        )
        
        if order_result and order_result.get("success"):
            self.open_positions[token_id] = {
                "entry_price": price,
                "target_price": price * self.target_multiplier,
                "shares": shares,
                "opportunity": opportunity
            }
            logger.info(f"✅ הצלחתי להיכנס ב-${price:.4f}")
            return True
        return False

    async def check_exit(self, token_id: str, current_price: float) -> bool:
        if token_id not in self.open_positions: return False
        pos = self.open_positions[token_id]
        if current_price >= pos["target_price"]:
            logger.info(f"🎉 יעד הושג! מנסה למכור ב-${current_price:.4f}")
            # כאן תבוצע המכירה באותו אופן
            del self.open_positions[token_id]
            return True
        return False