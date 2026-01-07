# simple_bot.py
"""
בוט פשוט להכפלת השקעות בפוליימרקט
מחפש מחירים קיצוניים (0.04 או 99.6), נכנס, ומנסה להכפיל ולצאת
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Set
import signal

from .simple_scanner import scan_extreme_price_markets, get_current_price
from .simple_trader import SimpleTrader
from .executor import OrderExecutor
from .logging_config import setup_logging

logger = logging.getLogger(__name__)


class SimpleCryptoBot:
    """
    בוט פשוט:
    1. סורק שווקי קריפטו עם מחירים קיצוניים
    2. קונה במחיר נמוך (0.04)
    3. מוכר בהכפלה (0.08)
    4. עוקב אחרי פוזיציות פתוחות
    """
    
    def __init__(
        self, 
        position_size_usd: float = 10.0,
        scan_interval_seconds: int = 300,
        price_check_interval_seconds: int = 30
    ):
        """
        Args:
            position_size_usd: כמה $ להשקיע בכל עסקה
            scan_interval_seconds: כל כמה זמן לסרוק שווקים חדשים (ברירת מחדל: 5 דקות)
            price_check_interval_seconds: כל כמה זמן לבדוק מחירים של פוזיציות פתוחות (30 שניות)
        """
        self.position_size_usd = position_size_usd
        self.scan_interval = scan_interval_seconds
        self.price_check_interval = price_check_interval_seconds
        
        # רכיבים
        self.executor = OrderExecutor()
        self.trader = SimpleTrader(self.executor, position_size_usd)
        
        # מעקב
        self.seen_opportunities: Set[str] = set()  # למנוע כניסות כפולות
        self.running = True
        
        # סטטיסטיקות
        self.stats = {
            "scans": 0,
            "opportunities_found": 0,
            "positions_entered": 0,
            "positions_exited": 0,
            "total_pnl": 0.0
        }
        
        logger.info("🚀 SimpleCryptoBot initialized")
        logger.info(f"💰 Position size: ${position_size_usd}")
        logger.info(f"⏱️  Scan interval: {scan_interval_seconds}s")
    
    async def start(self):
        """מתחיל את הבוט."""
        logger.info("=" * 60)
        logger.info("🤖 SimpleCryptoBot STARTED")
        logger.info("=" * 60)
        
        # בדוק יתרה
        balance = await self.executor.get_usdc_balance()
        logger.info(f"💵 Balance: ${balance:.2f} USDC")
        
        if balance < self.position_size_usd:
            logger.warning(f"⚠️ Balance (${balance:.2f}) < Position size (${self.position_size_usd:.2f})")
            logger.warning("⚠️ Bot will run but may not be able to enter trades")
        
        # הרץ שתי משימות במקביל
        try:
            await asyncio.gather(
                self._scan_loop(),      # סריקת שווקים חדשים
                self._monitor_loop()    # מעקב אחרי פוזיציות פתוחות
            )
        except KeyboardInterrupt:
            logger.info("⏹️  Shutting down...")
            self.running = False
    
    async def _scan_loop(self):
        """לולאה שסורקת שווקים חדשים."""
        while self.running:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"🔍 סריקה #{self.stats['scans'] + 1} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info(f"{'='*60}")
                
                # סרוק שווקים
                opportunities = scan_extreme_price_markets(
                    min_hours_until_close=1,      # לפחות שעה עד סגירה
                    max_entry_price=0.20,         # קנה עד 20 סנט
                    exit_multiplier=2.0,          # מכור ב-X2 (40 סנט)
                    focus_crypto=False            # כל השווקים (לא רק קריפטו)
                )
                
                self.stats["scans"] += 1
                self.stats["opportunities_found"] += len(opportunities)
                
                if not opportunities:
                    logger.info("😴 לא נמצאו הזדמנויות. ממתין...")
                else:
                    logger.info(f"🎯 נמצאו {len(opportunities)} הזדמנויות!")
                    
                    # נסה להיכנס להזדמנויות חדשות
                    for opp in opportunities:
                        token_id = opp["token_id"]
                        
                        # דלג אם כבר ראינו את זה
                        if token_id in self.seen_opportunities:
                            continue
                        
                        self.seen_opportunities.add(token_id)
                        
                        # נסה להיכנס
                        entered = await self.trader.check_entry(opp)
                        if entered:
                            self.stats["positions_entered"] += 1
                        
                        # השהה קצת בין עסקאות
                        await asyncio.sleep(2)
                
                # הצג סטטיסטיקות
                logger.info(f"\n📊 סטטיסטיקות:")
                logger.info(f"   סריקות: {self.stats['scans']}")
                logger.info(f"   הזדמנויות שנמצאו: {self.stats['opportunities_found']}")
                logger.info(f"   פוזיציות שנפתחו: {self.stats['positions_entered']}")
                logger.info(f"   פוזיציות שנסגרו: {self.stats['positions_exited']}")
                logger.info(self.trader.get_open_positions_summary())
                
                # המתן עד הסריקה הבאה
                logger.info(f"\n⏳ ממתין {self.scan_interval} שניות עד הסריקה הבאה...")
                await asyncio.sleep(self.scan_interval)
            
            except Exception as e:
                logger.error(f"❌ שגיאה בלולאת הסריקה: {e}", exc_info=True)
                await asyncio.sleep(30)  # המתן קצת ונסה שוב
    
    async def _monitor_loop(self):
        """לולאה שעוקבת אחרי פוזיציות פתוחות."""
        await asyncio.sleep(10)  # המתן קצת כדי לתת לסריקה הראשונה להסתיים
        
        while self.running:
            try:
                # אם אין פוזיציות פתוחות - אין מה לעקוב
                if not self.trader.open_positions:
                    await asyncio.sleep(self.price_check_interval)
                    continue
                
                logger.debug(f"👀 בודק {len(self.trader.open_positions)} פוזיציות פתוחות...")
                
                # עבור כל פוזיציה פתוחה
                for token_id in list(self.trader.open_positions.keys()):
                    # קבל מחיר נוכחי
                    current_price = get_current_price(token_id)
                    
                    if current_price is None:
                        logger.warning(f"⚠️ לא הצלחתי לקבל מחיר עבור {token_id}")
                        continue
                    
                    # בדוק אם צריך לצאת
                    exited = await self.trader.check_exit(token_id, current_price)
                    if exited:
                        self.stats["positions_exited"] += 1
                
                await asyncio.sleep(self.price_check_interval)
            
            except Exception as e:
                logger.error(f"❌ שגיאה בלולאת המעקב: {e}", exc_info=True)
                await asyncio.sleep(30)
    
    def stop(self):
        """עצירה מסודרת של הבוט."""
        logger.info("🛑 Stopping bot...")
        self.running = False


async def main():
    """נקודת כניסה ראשית."""
    # הגדר logging
    setup_logging()
    
    # צור בוט
    bot = SimpleCryptoBot(
        position_size_usd=10.0,           # $10 לעסקה
        scan_interval_seconds=300,        # סרוק כל 5 דקות
        price_check_interval_seconds=30   # בדוק מחירים כל 30 שניות
    )
    
    # טיפול ב-Ctrl+C
    def signal_handler(sig, frame):
        logger.info("\n⚠️  Ctrl+C detected")
        bot.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # הרץ
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
