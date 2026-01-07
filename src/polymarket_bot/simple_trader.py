# simple_trader.py
"""מנהל פשוט לכניסה ויציאה מעסקאות - אסטרטגיית הכפלה"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
from .executor import OrderExecutor

logger = logging.getLogger(__name__)


class SimpleTrader:
    """
    מנהל עסקאות פשוט:
    1. קונה במחיר קיצוני (0.04 או 0.996)
    2. מוכר בהכפלה (0.08 או 0.998)
    """
    
    def __init__(self, executor: OrderExecutor, position_size_usd: float = 10.0):
        """
        Args:
            executor: מנהל הפקודות
            position_size_usd: כמה דולר להשקיע בכל עסקה
        """
        self.executor = executor
        self.position_size_usd = position_size_usd
        self.open_positions: Dict[str, Dict] = {}  # token_id -> position_info
        
        # הגדרות
        self.target_multiplier = 2.0  # מכפיל יעד (2x = הכפלה)
        
        logger.info(f"💼 SimpleTrader initialized: ${position_size_usd}/trade, 2x target")
    
    async def check_entry(self, opportunity: Dict) -> bool:
        """
        בודק האם כדאי להיכנס לעסקה.
        
        Args:
            opportunity: הזדמנות מה-scanner
        
        Returns:
            True אם נכנסנו לעסקה
        """
        token_id = opportunity["token_id"]
        
        # אם כבר יש פוזיציה פתוחה - דלג
        if token_id in self.open_positions:
            return False
        
        current_price = opportunity["current_price"]
        
        # ודא שהמחיר באמת קיצוני
        if not (current_price <= 0.10 or current_price >= 0.90):
            return False
        
        # כמה יחידות לקנות
        shares = int(self.position_size_usd / current_price)
        if shares < 1:
            logger.warning(f"⚠️ לא מספיק תקציב: ${self.position_size_usd} / ${current_price}")
            return False
        
        # נסה לקנות
        logger.info(f"🎯 נכנס לעסקה: {opportunity['market_question'][:60]}")
        logger.info(f"   {opportunity['outcome']} @ ${current_price:.4f} | {shares} יחידות")
        
        order_result = self.executor.execute_trade(
            token_id=token_id,
            side="BUY",
            size=shares,
            price=current_price
        )
        
        if order_result and order_result.get("success"):
            # שמור את הפוזיציה
            self.open_positions[token_id] = {
                "opportunity": opportunity,
                "entry_price": current_price,
                "target_price": current_price * self.target_multiplier,
                "shares": shares,
                "entry_time": datetime.now().isoformat(),
                "order_id": order_result.get("order_id")
            }
            
            logger.info(f"✅ נכנסתי ב-${current_price:.4f} | יעד: ${self.open_positions[token_id]['target_price']:.4f}")
            return True
        
        else:
            logger.error(f"❌ כניסה נכשלה: {order_result}")
            return False
    
    async def check_exit(self, token_id: str, current_price: float) -> bool:
        """
        בודק האם צריך לצאת מפוזיציה (רווח בלבד).
        
        Args:
            token_id: מזהה ה-token
            current_price: המחיר הנוכחי
        
        Returns:
            True אם יצאנו מהפוזיציה
        """
        if token_id not in self.open_positions:
            return False
        
        position = self.open_positions[token_id]
        entry_price = position["entry_price"]
        target_price = position["target_price"]
        shares = position["shares"]
        
        # בדוק האם הגענו ליעד (הכפלה!)
        if current_price >= target_price:
            logger.info(f"🎉 יעד הושג! ${entry_price:.4f} → ${current_price:.4f}")
            return await self._exit_position(token_id, current_price, "TARGET_REACHED")
        
        return False
    
    async def _exit_position(self, token_id: str, exit_price: float, reason: str) -> bool:
        """
        יוצא מפוזיציה.
        
        Args:
            token_id: מזהה ה-token
            exit_price: מחיר היציאה
            reason: סיבת היציאה
        
        Returns:
            True אם היציאה הצליחה
        """
        if token_id not in self.open_positions:
            return False
        
        position = self.open_positions[token_id]
        shares = position["shares"]
        entry_price = position["entry_price"]
        
        # מכור
        order_result = self.executor.execute_trade(
            token_id=token_id,
            side="SELL",
            size=shares,
            price=exit_price
        )
        
        if order_result and order_result.get("success"):
            # חשב רווח/הפסד
            pnl = shares * (exit_price - entry_price)
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            
            logger.info(f"💰 יצאתי: {reason}")
            logger.info(f"   רווח/הפסד: ${pnl:.2f} ({pnl_percent:+.1f}%)")
            
            # הסר מרשימת הפוזיציות
            del self.open_positions[token_id]
            return True
        
        else:
            logger.error(f"❌ יציאה נכשלה: {order_result}")
            return False
    
    def get_open_positions_summary(self) -> str:
        """מחזיר סיכום של הפוזיציות הפתוחות."""
        if not self.open_positions:
            return "אין פוזיציות פתוחות"
        
        summary = f"\n📊 {len(self.open_positions)} פוזיציות פתוחות:\n"
        for token_id, pos in self.open_positions.items():
            opp = pos["opportunity"]
            summary += (
                f"  • {opp['market_question'][:50]}\n"
                f"    כניסה: ${pos['entry_price']:.4f} | יעד: ${pos['target_price']:.4f}\n"
            )
        return summary
