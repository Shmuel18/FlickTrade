# simple_bot.py
import asyncio
import logging
from .simple_scanner import scan_extreme_price_markets, get_current_price
from .config import PORTFOLIO_PERCENT, MIN_POSITION_USD
from .simple_trader import SimpleTrader
from .executor import OrderExecutor
from .logging_config import setup_logging
from .config import BUY_PRICE_THRESHOLD, SELL_MULTIPLIER

logger = logging.getLogger(__name__)

class SimpleCryptoBot:
    def __init__(self):
        self.executor = OrderExecutor()
        self.trader = None  # יאותחל אחרי שנקבל את היתרה
        self.seen_opportunities = set()
        self.running = True
        self.position_size = MIN_POSITION_USD  # ברירת מחדל

    async def _init_position_size(self):
        """מחשב גודל פוזיציה לפי אחוז מהתיק"""
        try:
            balance = await self.executor.get_usdc_balance()
            calculated_size = balance * PORTFOLIO_PERCENT  # 0.5% מהתיק
            self.position_size = max(calculated_size, MIN_POSITION_USD)  # מינימום $1
            logger.info(f"💰 יתרה: ${balance:.2f} | גודל פוזיציה: ${self.position_size:.2f} ({PORTFOLIO_PERCENT*100}%)")
        except Exception as e:
            logger.warning(f"⚠️ לא הצלחתי לקבל יתרה: {e}, משתמש בברירת מחדל ${MIN_POSITION_USD}")
            self.position_size = MIN_POSITION_USD
        
        self.trader = SimpleTrader(self.executor, self.position_size)

    async def _scan_loop(self):
        while self.running:
            try:
                # הגדרות: סורק הכל עם threshold מהקונפיג
                logger.info(f"🔍 סורק שווקים עם threshold: ${BUY_PRICE_THRESHOLD}")
                opps = scan_extreme_price_markets(
                    min_hours_until_close=1, 
                    low_price_threshold=BUY_PRICE_THRESHOLD,
                    focus_crypto=False
                )
                
                for opp in opps:
                    if opp["token_id"] not in self.seen_opportunities:
                        self.seen_opportunities.add(opp["token_id"])
                        await self.trader.check_entry(opp)
                
                await asyncio.sleep(300) # סריקה כל 5 דקות
            except Exception as e:
                logger.error(f"שגיאה בסריקה: {e}")
                await asyncio.sleep(60)

    async def start(self):
        await self._init_position_size()  # מחשב גודל פוזיציה לפי יתרה
        logger.info(f"🚀 הבוט התחיל סריקה גלובלית למחירים ≤ ${BUY_PRICE_THRESHOLD}")
        logger.info(f"📊 מכפיל מכירה: {SELL_MULTIPLIER}x (target: ${BUY_PRICE_THRESHOLD * SELL_MULTIPLIER})")
        await asyncio.gather(self._scan_loop())

async def main():
    setup_logging()
    bot = SimpleCryptoBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())