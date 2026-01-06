# main.py
import asyncio
from scanner import scan_polymarket_for_hierarchical_markets
from ws_manager import WebSocketManager
from executor import OrderExecutor

async def price_update_handler(token_id, price):
    # כאן תוכנס בעתיד הלוגיקה של logic.py לבדיקת ארביטראז'
    print(f"Price update for {token_id}: {price}")

async def main():
    markets = scan_polymarket_for_hierarchical_markets()
    if not markets:
        print("No markets found.")
        return

    ws = WebSocketManager()
    await ws.connect()

    for event, data in markets.items():
        for token_id in data["clob_token_ids"]:
            await ws.subscribe(token_id)

    print("--- Starting Live Monitoring ---")
    await ws.receive_data(price_update_handler)

if __name__ == "__main__":
    asyncio.run(main())