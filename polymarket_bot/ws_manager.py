# ws_manager.py
import asyncio
import websockets
import json
from config import CLOB_WS_URL

class WebSocketManager:
    def __init__(self):
        self.ws = None
        self.prices = {}

    async def connect(self):
        self.ws = await websockets.connect(CLOB_WS_URL)
        print("Connected to CLOB WebSocket.")

    async def subscribe(self, clob_token_id):
        payload = {
            "type": "subscribe",
            "channels": ["order_book"],
            "clobTokenIds": [clob_token_id]
        }
        await self.ws.send(json.dumps(payload))
        print(f"Subscribed to: {clob_token_id}")

    async def receive_data(self, callback):
        async for message in self.ws:
            data = json.loads(message)
            # חילוץ מחיר ה-Yes (ה-Bid הכי גבוה)
            if "bids" in data and len(data["bids"]) > 0:
                token_id = data.get("asset_id")
                price = float(data["bids"][0][0])
                self.prices[token_id] = price
                await callback(token_id, price)