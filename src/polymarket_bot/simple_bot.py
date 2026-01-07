# simple_bot.py
import asyncio
import logging
from .simple_scanner import scan_extreme_price_markets, get_current_price
from .simple_trader import SimpleTrader
from .executor import OrderExecutor
from .logging_config import setup_logging
from .config import BUY_PRICE_THRESHOLD, SELL_MULTIPLIER

logger = logging.getLogger(__name__)

class SimpleCryptoBot:
    def __init__(self, position_size_usd: float = 10.0):
        self.executor = OrderExecutor()
        self.trader = SimpleTrader(self.executor, position_size_usd)
        self.seen_opportunities = set()
        self.running = True

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
        logger.info(f"🚀 הבוט התחיל סריקה גלובלית למחירים ≤ ${BUY_PRICE_THRESHOLD}")
        logger.info(f"📊 מכפיל מכירה: {SELL_MULTIPLIER}x (target: ${BUY_PRICE_THRESHOLD * SELL_MULTIPLIER})")
        await asyncio.gather(self._scan_loop())

async def main():
    setup_logging()
    bot = SimpleCryptoBot(position_size_usd=10.0)
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())