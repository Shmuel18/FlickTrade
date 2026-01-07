# ws_manager.py
import asyncio
import websockets
import json
import logging
from typing import Callable, Dict, Optional, List, Any
from .config import CLOB_WS_URL, WS_PING_INTERVAL, WS_PING_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)

class WebSocketManager:
    """ניהול חיבור ה-WebSocket ל-Polymarket CLOB לקבלת עדכוני מחירים בזמן אמת."""
    
    def __init__(self):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.prices: Dict[str, float] = {}
        self.subscribed_tokens: set = set()
        self.reconnect_count = 0

    async def connect(self, retry_count: int = 0) -> bool:
        """יצירת חיבור עם מנגנון התחברות מחדש אוטומטי."""
        try:
            logger.info(f"Connecting to CLOB WebSocket: {CLOB_WS_URL}")
            self.ws = await asyncio.wait_for(
                websockets.connect(
                    CLOB_WS_URL,
                    ping_interval=WS_PING_INTERVAL,
                    ping_timeout=WS_PING_TIMEOUT,
                    close_timeout=10
                ),
                timeout=15
            )
            logger.info("[CONNECT] Connected to CLOB WebSocket")
            self.reconnect_count = 0
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            if retry_count < MAX_RETRIES:
                wait_time = 2 ** retry_count
                await asyncio.sleep(wait_time)
                return await self.connect(retry_count + 1)
            return False

    async def subscribe(self, clob_token_ids: List[str]) -> bool:
        """הרשמה לרשימת טוקנים בהתאם למפרט ה-CLOB."""
        if not self.ws:
            return False
        try:
            to_subscribe = [str(tid) for tid in clob_token_ids if tid and str(tid) not in self.subscribed_tokens]
            if not to_subscribe:
                return True

            payload = {
                "type": "market",
                "operation": "subscribe",  # קריטי למניעת INVALID OPERATION
                "assets_ids": to_subscribe
            }
            await self.ws.send(json.dumps(payload))
            self.subscribed_tokens.update(to_subscribe)
            return True
        except Exception as e:
            logger.error(f"❌ Subscription failed: {e}")
            return False
    
    async def subscribe_batch(self, token_ids: List[str]) -> int:
        """חלוקת הטוקנים לקבוצות של 100 למניעת חסימות שרת."""
        if not token_ids: return 0
        chunk_size = 100
        success_total = 0
        for i in range(0, len(token_ids), chunk_size):
            chunk = token_ids[i:i + chunk_size]
            if await self.subscribe(chunk):
                success_total += len(chunk)
            await asyncio.sleep(0.1)
        return success_total

    async def receive_data(self, callback: Callable) -> None:
        """קליטה ועיבוד של נתוני השוק מפורמט price_changes."""
        if not self.ws: return
        try:
            async for message in self.ws:
                if not message or message == "PONG": continue
                try:
                    data = json.loads(message)
                except: continue
                
                messages = data if isinstance(data, list) else [data]
                for msg in messages:
                    if not isinstance(msg, dict): continue
                    
                    # טיפול בפורמט price_changes שראינו בלוגים
                    if "price_changes" in msg:
                        for change in msg["price_changes"]:
                            token_id = change.get("asset_id")
                            # חילוץ ה-best_bid שהוא המחיר הרלוונטי למסחר
                            price_val = change.get("best_bid") or change.get("price")
                            if token_id and price_val:
                                price = float(price_val)
                                if 0 <= price <= 1:
                                    self.prices[token_id] = price
                                    await callback(token_id, price)
                    # גיבוי לפורמט bids
                    elif "bids" in msg and msg["bids"]:
                        token_id = msg.get("asset_id")
                        price = float(msg["bids"][0][0])
                        if token_id and 0 <= price <= 1:
                            self.prices[token_id] = price
                            await callback(token_id, price)
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")

    async def close(self) -> None:
        if self.ws:
            try:
                await asyncio.wait_for(self.ws.close(), timeout=2.0)
            except: pass
            finally: self.ws = None