# executor.py
from py_clob_client.client import ClobClient
from config import CLOB_URL, API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY, CHAIN_ID

class OrderExecutor:
    def __init__(self):
        # תיקון השגיאה: שימוש בשמות הפרמטרים הנכונים שה-SDK מצפה להם
        self.client = ClobClient(
            host=CLOB_URL,
            key=API_KEY,
            secret=API_SECRET,
            passphrase=API_PASSPHRASE,
            private_key=PRIVATE_KEY,
            chain_id=CHAIN_ID
        )

    async def execute_trade(self, clob_token_id, side, size, price):
        try:
            # יצירת הזמנה חדשה
            order = self.client.create_order(
                clob_token_id=clob_token_id,
                side=side,
                size=size,
                price=price,
                order_type='limit'
            )
            print(f"Order placed: {order}")
            return order
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None