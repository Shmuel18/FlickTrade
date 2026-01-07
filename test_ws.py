#!/usr/bin/env python3
"""Quick test of WebSocket subscription with correct format."""

import asyncio
import websockets
import json

async def test_ws():
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    print(f"Connecting to {url}...")
    
    async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
        print("✓ Connected!")
        
        # Send subscription with correct format from Polymarket docs
        # According to research: type="market", assets_ids=[...]
        sample_tokens = [
            "0x1234567890123456789012345678901234567890",  # Placeholder token IDs
            "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        ]
        
        payload = {
            "type": "market",
            "assets_ids": sample_tokens
        }
        
        print(f"\nSending subscription: {json.dumps(payload, indent=2)}")
        await ws.send(json.dumps(payload))
        
        print("\nListening for 30 seconds...")
        message_count = 0
        try:
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=30)
                    message_count += 1
                    
                    # Show first 25 messages and then every 100th
                    if message_count <= 25 or message_count % 100 == 0:
                        print(f"\n[Message #{message_count}]")
                        print(f"Raw: {message[:300]}")
                        
                        try:
                            data = json.loads(message)
                            if isinstance(data, list):
                                print(f"Type: List with {len(data)} items")
                                if len(data) > 0:
                                    print(f"First item: {data[0]}")
                            else:
                                print(f"Type: {type(data).__name__}")
                                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                        except:
                            print("Not valid JSON")
                            
                except asyncio.TimeoutError:
                    print(f"\nTimeout after 30 seconds. Received {message_count} messages total.")
                    break
        except KeyboardInterrupt:
            print(f"\n\nStopped. Received {message_count} messages total.")

if __name__ == "__main__":
    asyncio.run(test_ws())
