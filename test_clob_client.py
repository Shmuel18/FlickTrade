# test_clob_client.py
"""בודק איך לקבל מחירים דרך py_clob_client"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from polymarket_bot.config import API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY, CLOB_URL, CHAIN_ID, FUNDER_ADDRESS

# יצירת client
creds = ApiCreds(
    api_key=API_KEY.strip(),
    api_secret=API_SECRET.strip(),
    api_passphrase=API_PASSPHRASE.strip()
)

client = ClobClient(
    host=CLOB_URL,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    creds=creds,
    signature_type=1,
    funder=FUNDER_ADDRESS
)

# נסה לקבל מידע על שוק
token_id = "93592949212798121127213117304912625505836768562433217537850469496310204567695"

print(f"🔍 מנסה לקבל order book עבור token...")
try:
    book = client.get_order_book(token_id)
    print(f"✅ Order Book:")
    print(f"   Bids: {len(book.get('bids', []))}")
    print(f"   Asks: {len(book.get('asks', []))}")
    
    if book.get('bids'):
        best_bid = book['bids'][0]
        print(f"   Best Bid: {best_bid.get('price')}")
    
    if book.get('asks'):
        best_ask = book['asks'][0]
        print(f"   Best Ask: {best_ask.get('price')}")
        
except Exception as e:
    print(f"❌ שגיאה: {e}")

print()

# נסה גם לקבל last trade price
print(f"🔍 מנסה לקבל last trade price...")
try:
    # נסה לקבל trades
    trades = client.get_trades(token_id)
    if trades:
        print(f"✅ מצאתי {len(trades)} trades")
        if trades:
            last_trade = trades[0]
            print(f"   Last Trade Price: {last_trade.get('price')}")
except Exception as e:
    print(f"❌ שגיאה: {e}")
