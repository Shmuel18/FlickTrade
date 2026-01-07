# main.py
import asyncio
import logging
import signal
import sys
import websockets
from datetime import datetime
from typing import Dict, List, Optional, Set

from .logging_config import setup_logging
from .scanner import scan_polymarket_for_hierarchical_markets
from .ws_manager import WebSocketManager
from .logic import check_arbitrage
from .executor import OrderExecutor
from .persistence import TransactionLogger, PerformanceMonitor
from .config import MARKET_SCAN_INTERVAL

logger = logging.getLogger(__name__)

class PolymarketBot:
    """Main trading bot orchestrator."""
    
    def __init__(self):
        self.ws = WebSocketManager()
        self.executor = OrderExecutor()  # Initialize the executor for trade execution
        self.transaction_logger = TransactionLogger()  # CSV logging
        self.performance_monitor = PerformanceMonitor(self.transaction_logger)
        self.current_prices: Dict[str, float] = {}
        self.price_timestamps: Dict[str, float] = {}  # Track price freshness
        self.active_pairs: List[Dict] = []
        self.subscribed_tokens: Set[str] = set()
        self.last_scan_time = 0
        self.running = True
        self.shutdown_event = asyncio.Event()
        self._show_dry_run = False  # Set to True to see what trades would be made
        # State machine to prevent duplicate trades
        self.last_trade_attempt: Dict[str, float] = {}  # event_id -> timestamp
        self.trade_cooldown = 60  # seconds between trades on same event
        self.stats = {
            'opportunities_found': 0,
            'trades_executed': 0,
            'total_pnl': 0.0,
            'price_updates': 0,
            'missed_no_balance': 0,  # Track missed opportunities
            'total_missed_profit': 0.0
        }
    
    async def on_price_update(self, token_id: str, price: float) -> None:
        """Handle incoming price update from WebSocket.
        
        Args:
            token_id: Token ID that was updated
            price: New bid price
        """
        current_time = asyncio.get_event_loop().time()
        self.current_prices[token_id] = price
        self.price_timestamps[token_id] = current_time  # Track freshness
        self.stats['price_updates'] += 1
        
        # Check for arbitrage opportunities
        opportunities = check_arbitrage(self.active_pairs, self.current_prices)
        
        if opportunities:
            self.stats['opportunities_found'] += len(opportunities)
            for opp in opportunities:
                await self.handle_opportunity(opp)
    
    async def handle_opportunity(self, opportunity: Dict) -> None:
        """Process and potentially execute an arbitrage opportunity."""
        try:
            event_id = opportunity['event']
            # Enhanced dedup key: include token pair
            pair_key = (event_id, opportunity['easy_condition_id'], opportunity['hard_condition_id'])
            current_time = asyncio.get_event_loop().time()
            
            # Check if we recently traded this exact pair
            if pair_key in self.last_trade_attempt:
                time_since_last = current_time - self.last_trade_attempt[pair_key]
                if time_since_last < self.trade_cooldown:
                    # Skip silently - no need to log every cooldown
                    return
            
            logger.info(
                f"[OPPORTUNITY] {opportunity['event']} | "
                f"Profit: ${opportunity['profit_margin']:.4f} "
                f"({opportunity['profit_pct']:.2f}%) | "
                f"Strategy: {opportunity['strategy']}"
            )
            
            # Execute trade if executor is initialized
            if self.executor:
                # Check price freshness (prices should be recent)
                easy_price_data = self.price_timestamps.get(opportunity['easy_condition_id'])
                hard_price_data = self.price_timestamps.get(opportunity['hard_condition_id'])
                
                if easy_price_data and hard_price_data:
                    age_easy = current_time - easy_price_data
                    age_hard = current_time - hard_price_data
                    max_price_age = 60  # seconds (increased from 10 for political markets)
                    
                    if age_easy > max_price_age or age_hard > max_price_age:
                        logger.warning(f"[SKIP] Prices too stale. Easy: {age_easy:.1f}s, Hard: {age_hard:.1f}s")
                        return
                
                # Update last attempt timestamp with pair key
                self.last_trade_attempt[pair_key] = current_time
                
                # Calculate order size with proper cap
                await self.executor.get_usdc_balance()
                
                # Check if we have real balance (not default)
                # Don't fetch every time - use cached value from startup
                if not hasattr(self.executor, '_balance_is_real') or not self.executor._balance_is_real or self.executor.usdc_balance <= 5.0:
                    # Track missed opportunity
                    self.stats['missed_no_balance'] += 1
                    estimated_investment = 5.0  # Minimum
                    estimated_profit = opportunity['profit_margin'] * (estimated_investment / opportunity['easy_price'])
                    self.stats['total_missed_profit'] += estimated_profit
                    
                    # Show missed info occasionally (not every time to reduce logs)
                    if self.stats['missed_no_balance'] % 10 == 1:  # Every 10th opportunity
                        logger.warning(f"⚠️ Balance too low - skipping trade")
                        logger.info(f"   💡 [MISSED] Could have made ${estimated_profit:.4f} ({opportunity['profit_pct']:.2f}%)")
                        logger.info(f"   💡 Total missed so far: {self.stats['missed_no_balance']} opportunities, ${self.stats['total_missed_profit']:.2f} potential profit")
                    return
                
                # Risk management: 1% of portfolio per trade (conservative)
                max_usdc_per_trade = self.executor.usdc_balance * 0.01  # 1% per trade
                min_usdc_per_trade = 5.0  # $5 minimum (Polymarket requires min 5 shares)
                max_position_cap = 20.0  # $20 hard cap per trade (lower risk)
                
                # Calculate actual USDC to use
                usdc_to_use = min(max_usdc_per_trade, max_position_cap)
                
                # If 1% is less than $5, use $5 (but only if we have enough)
                if usdc_to_use < min_usdc_per_trade:
                    if self.executor.usdc_balance >= min_usdc_per_trade:
                        usdc_to_use = min_usdc_per_trade
                    else:
                        logger.warning(f"⚠️ Insufficient balance for minimum trade size")
                        return
                
                # Calculate shares needed
                order_size = usdc_to_use / opportunity['easy_price']
                
                # Verify we can afford both legs
                total_cost = (order_size * opportunity['easy_price']) + (order_size * (1 - opportunity['hard_price']))
                if total_cost > self.executor.usdc_balance * 0.95:  # Keep 5% buffer
                    logger.warning(f"⚠️ Total cost (${total_cost:.2f}) exceeds available balance")
                    return
                
                logger.info(
                    f"[EXECUTE] Position sizing:\n"
                    f"   Available Balance: ${self.executor.usdc_balance:.2f}\n"
                    f"   Position Size (1%): ${max_usdc_per_trade:.2f}\n"
                    f"   Actual Investment: ${usdc_to_use:.2f} (per leg)\n"
                    f"   Total Cost (2 legs): ${total_cost:.2f}\n"
                    f"   Shares: {order_size:.2f}\n"
                    f"   Easy leg (YES): {opportunity['easy_condition_id'][:8]}... @ ${opportunity['easy_price']:.4f}\n"
                    f"   Hard leg (NO): {opportunity['hard_condition_id'][:8]}... @ ${(1-opportunity['hard_price']):.4f}"
                )
                
                # Execute arbitrage in thread to avoid blocking event loop
                success = await asyncio.to_thread(
                    self.executor.execute_arbitrage, 
                    opportunity, 
                    order_size
                )
                
                if success:
                    self.stats['trades_executed'] += 1
                    profit = opportunity['profit_margin'] * order_size
                    self.stats['total_pnl'] += profit
                    logger.info(
                        f"✅ [SUCCESS] Arbitrage executed!\n"
                        f"   Event: {opportunity['event']}\n"
                        f"   Leg 1 (Easy YES): {order_size:.2f} shares @ ${opportunity['easy_price']:.4f}\n"
                        f"   Leg 2 (Hard NO): {order_size:.2f} shares @ ${(1-opportunity['hard_price']):.4f}\n"
                        f"   Total Investment: ${total_cost:.2f}\n"
                        f"   Expected Profit: ${profit:.4f} ({opportunity['profit_pct']:.2f}%)"
                    )
                    
                    # Log to CSV for persistence
                    if self.executor and hasattr(self.executor, 'transactions'):
                        for tx in self.executor.transactions.values():
                            self.transaction_logger.log_transaction(tx, opportunity)
                            self.performance_monitor.session_stats['trades_successful'] += 1
                else:
                    logger.warning(f"⚠️ [FAILED] Trade execution failed for {event_id}")
                    self.performance_monitor.session_stats['trades_attempted'] += 1
            else:
                logger.warning("[WARNING] Executor not initialized - opportunity logged only")
                
        except Exception as e:
            logger.error(f"Error handling opportunity: {e}")
    
    async def scan_and_subscribe(self) -> bool:
        """Scan for hierarchical markets and subscribe to tokens.
        
        Returns:
            True if markets found and subscriptions successful
        """
        try:
            logger.info("[SCAN] Searching for hierarchical markets...")
            # Run blocking scan in thread to avoid blocking event loop
            markets = await asyncio.to_thread(scan_polymarket_for_hierarchical_markets)
            
            if not markets:
                logger.warning("[SCAN] No hierarchical markets found")
                return False
            
            # Build pairs from hierarchical markets
            self.active_pairs = []
            new_tokens = set()
            
            for event_title, market_data in markets.items():
                token_ids = market_data.get("clob_token_ids", [])
                all_tokens_list = market_data.get("all_token_ids", [])
                
                # Create pairs from hierarchical markets
                for i in range(len(token_ids) - 1):
                    pair = {
                        'event_title': event_title,
                        'parent_id': token_ids[i],
                        'child_id': token_ids[i + 1],
                        'parent_all_tokens': all_tokens_list[i] if i < len(all_tokens_list) else [],
                        'child_all_tokens': all_tokens_list[i + 1] if i + 1 < len(all_tokens_list) else []
                    }
                    self.active_pairs.append(pair)
                    # Subscribe to ALL tokens for each market (YES + NO)
                    if i < len(all_tokens_list) and all_tokens_list[i]:
                        # Handle case where all_tokens_list[i] might be a string representation of a list
                        tokens_to_add = all_tokens_list[i]
                        if isinstance(tokens_to_add, str):
                            # Check if it's a JSON array string
                            if tokens_to_add.startswith('[') and tokens_to_add.endswith(']'):
                                try:
                                    import json
                                    tokens_to_add = json.loads(tokens_to_add)
                                except (json.JSONDecodeError, TypeError):
                                    logger.warning(f"Failed to parse tokens string: {tokens_to_add[:100]}")
                                    continue
                        if isinstance(tokens_to_add, list):
                            new_tokens.update(tokens_to_add)
                        elif isinstance(tokens_to_add, str):
                            # Single token
                            new_tokens.add(tokens_to_add)
                        else:
                            logger.warning(f"Unexpected token format: {type(tokens_to_add)} - {tokens_to_add[:100] if isinstance(tokens_to_add, str) else tokens_to_add}")
                    
                    if i + 1 < len(all_tokens_list) and all_tokens_list[i + 1]:
                        tokens_to_add = all_tokens_list[i + 1]
                        if isinstance(tokens_to_add, str):
                            # Check if it's a JSON array string
                            if tokens_to_add.startswith('[') and tokens_to_add.endswith(']'):
                                try:
                                    import json
                                    tokens_to_add = json.loads(tokens_to_add)
                                except (json.JSONDecodeError, TypeError):
                                    logger.warning(f"Failed to parse tokens string: {tokens_to_add[:100]}")
                                    continue
                        if isinstance(tokens_to_add, list):
                            new_tokens.update(tokens_to_add)
                        elif isinstance(tokens_to_add, str):
                            # Single token
                            new_tokens.add(tokens_to_add)
                        else:
                            logger.warning(f"Unexpected token format: {type(tokens_to_add)} - {tokens_to_add[:100] if isinstance(tokens_to_add, str) else tokens_to_add}")
            
            logger.info(
                f"[OK] Found {len(self.active_pairs)} pairs from {len(markets)} hierarchical markets"
            )
            logger.info(f"[INFO] Total unique tokens: {len(new_tokens)}")
            
            # Subscribe to tokens
            self.subscribed_tokens = new_tokens
            if self.ws.ws is None:
                logger.info("[CONNECT] Connecting to WebSocket...")
                if not await self.ws.connect():
                    logger.error("[ERROR] Failed to connect to WebSocket")
                    return False
            
            subscribed = await self.ws.subscribe_batch(list(new_tokens))
            logger.info(f"[CONNECT] Subscribed to {subscribed} tokens")
            
            return subscribed > 0
            
        except Exception as e:
            logger.error(f"[ERROR] Scanning markets: {e}")
            return False
    
    async def market_monitoring_loop(self) -> None:
        """Main monitoring loop - checks for market updates with reconnection."""
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self.running:
            try:
                # אם יש יותר מדי ניסיונות כושלים, עצור
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error(f"[FATAL] Failed to connect after {max_reconnect_attempts} attempts - stopping")
                    self.running = False
                    break
                
                # Ensure we have an active WebSocket connection
                if self.ws.ws is None:
                    reconnect_attempts += 1
                    if reconnect_attempts == 1:
                        logger.info("[RECONNECT] Reconnecting to WebSocket...")
                    if not await self.ws.connect():
                        if reconnect_attempts >= 3:
                            logger.warning(f"[RECONNECT] Attempt {reconnect_attempts}/{max_reconnect_attempts} failed")
                        await asyncio.sleep(30)
                        continue
                
                # איפוס מונה הניסיונות אחרי חיבור מוצלח
                reconnect_attempts = 0
                
                # Start receiving data
                await self.ws.receive_data(self.on_price_update)
                
            except asyncio.CancelledError:
                break
            except websockets.exceptions.ConnectionClosed:
                self.ws.ws = None  # Reset connection
                await asyncio.sleep(10)  # המתנה ארוכה יותר
            except Exception as e:
                if reconnect_attempts >= 3:
                    logger.warning(f"[ERROR] {str(e)[:50]}")
                self.ws.ws = None  # Reset connection on any error
                await asyncio.sleep(15)  # המתנה עוד יותר ארוכה
    
    async def periodic_rescan_loop(self) -> None:
        """Periodically scan for new markets (every hour)."""
        while self.running:
            try:
                await asyncio.wait_for(asyncio.sleep(MARKET_SCAN_INTERVAL), timeout=MARKET_SCAN_INTERVAL + 1)
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break
            
            if not self.running:
                break
                
            try:
                logger.info("[RESCAN] Periodic market update...")
                await self.scan_and_subscribe()
            except Exception as e:
                logger.error(f"[ERROR] Rescan loop: {e}")
    
    async def settlement_check_loop(self) -> None:
        """בדיקה תקופתית ושחרור פוזיציות בשווקים סגורים."""
        while self.running:
            try:
                await asyncio.wait_for(asyncio.sleep(600), timeout=601)  # כל 10 דקות
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break
            
            if not self.running:
                break
            
            try:
                if self.executor:
                    await self.executor.check_and_settle_positions()
            except Exception as e:
                logger.error(f"[ERROR] Settlement loop: {e}")
    
    async def stats_reporter_loop(self) -> None:
        """Periodically report bot statistics."""
        while self.running:
            try:
                await asyncio.wait_for(asyncio.sleep(300), timeout=301)  # Report every 5 minutes
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break
            
            if not self.running:
                break
                
            try:
                logger.info(
                    f"[STATS] Updates: {self.stats['price_updates']} | "
                    f"Opportunities: {self.stats['opportunities_found']} | "
                    f"Trades: {self.stats['trades_executed']} | "
                    f"P&L: ${self.stats['total_pnl']:.2f}"
                )
                
                # Show missed opportunities if any
                if self.stats['missed_no_balance'] > 0:
                    logger.info(
                        f"[MISSED] {self.stats['missed_no_balance']} opportunities due to no balance | "
                        f"Potential profit: ${self.stats['total_missed_profit']:.2f}"
                    )
                # Log to CSV for persistence
                self.performance_monitor.session_stats['price_updates'] = self.stats['price_updates']
                self.performance_monitor.session_stats['opportunities_found'] = self.stats['opportunities_found']
                self.performance_monitor.session_stats['total_pnl'] = self.stats['total_pnl']
            except Exception as e:
                logger.error(f"[ERROR] Stats loop: {e}")
    
    def shutdown(self, signum, frame) -> None:
        """Handle shutdown signal gracefully."""
        logger.info("\n[SHUTDOWN] Ctrl+C detected - cleaning up...")
        self.running = False
    
    async def run(self) -> None:
        """Main bot execution method."""
        # Register signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        logger.info("\n" + "="*60)
        logger.info("[START] POLYMARKET ARBITRAGE BOT")
        logger.info(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("[INFO] Press Ctrl+C to stop")
        logger.info("="*60 + "\n")
        
        # Initial market scan
        if not await self.scan_and_subscribe():
            logger.error("Failed to scan markets on startup")
            return
        
        # Check if we have real balance
        await self.executor.get_usdc_balance()
        if not hasattr(self.executor, '_balance_is_real') or not self.executor._balance_is_real:
            logger.warning("\n" + "="*60)
            logger.warning("⚠️  TRADING DISABLED - No balance available")
            logger.warning("="*60)
            logger.warning("Bot will monitor opportunities but not trade.")
            logger.warning("To enable: Add USDC to wallet and restart.")
            logger.warning("="*60 + "\n")
        
        # Create tasks with proper cancellation handling
        monitor_task = None
        rescan_task = None
        stats_task = None
        settlement_task = None
        
        try:
            monitor_task = asyncio.create_task(self.market_monitoring_loop())
            rescan_task = asyncio.create_task(self.periodic_rescan_loop())
            stats_task = asyncio.create_task(self.stats_reporter_loop())
            settlement_task = asyncio.create_task(self.settlement_check_loop())
            
            # Main loop - check if running every 100ms
            while self.running:
                await asyncio.sleep(0.1)
                
            # If we exit the loop, shutdown was signaled
            logger.info("[SHUTDOWN] Shutting down tasks...")
            
        except KeyboardInterrupt:
            logger.info("[SHUTDOWN] Keyboard interrupt")
            self.running = False
        finally:
            # Ensure all tasks are cancelled
            self.running = False
            
            tasks_to_cancel = [t for t in [monitor_task, rescan_task, stats_task, settlement_task] if t]
            for task in tasks_to_cancel:
                if not task.done():
                    task.cancel()
            
            # Wait for cancellation
            if tasks_to_cancel:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("[CLEANUP] Closing connections...")
        
        try:
            await self.ws.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")
        
        # Generate final performance report
        try:
            self.performance_monitor.report()
        except Exception as e:
            logger.error(f"Error generating report: {e}")
        
        logger.info("[DONE] Bot shutdown complete")


async def main():
    """Entry point for the bot."""
    # Initialize logging first
    setup_logging()
    
    bot = PolymarketBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())