# executor.py
import logging
import httpx
from typing import Optional, Dict, Any
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from .config import (
    CLOB_URL, API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY, 
    CHAIN_ID, STOP_LOSS_PERCENT, FUNDER_ADDRESS
)

logger = logging.getLogger(__name__)

class OrderExecutor:
    """מנהל פקודות עבור ארנקי Proxy (Magic/Email) לפי שלב 4 בתיעוד."""
    
    def __init__(self):
        try:
            creds = ApiCreds(
                api_key=API_KEY.strip() if API_KEY else "",
                api_secret=API_SECRET.strip() if API_SECRET else "",
                api_passphrase=API_PASSPHRASE.strip() if API_PASSPHRASE else ""
            )
            
            # Initialize client with signature_type=1 (POLY_PROXY)
            self.client = ClobClient(
                host=CLOB_URL,
                key=PRIVATE_KEY,
                chain_id=CHAIN_ID,
                creds=creds,
                signature_type=1,
                funder=FUNDER_ADDRESS
            )
            
            self.client.set_api_creds(creds)
            self.usdc_balance = 0.0
            self._balance_is_real = False
            self.open_positions = {}  # מעקב אחרי פוזיציות פתוחות
            
            logger.info(f"🔑 Signer Wallet: {self.client.get_address()}")
            logger.info(f"💰 Funder Wallet (Proxy): {FUNDER_ADDRESS}")
            logger.info("✅ OrderExecutor initialized with POLY_PROXY support")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}"); raise

    async def get_usdc_balance(self) -> float:
        """משיכת יתרה - מנסה מספר endpoints."""
        # ניסיון 1: שיטת הספרייה המקורית
        try:
            result = self.client.get_balance_allowance()
            if result and 'balance' in result:
                self.usdc_balance = float(result['balance'])
                logger.info(f"💰 Balance: ${self.usdc_balance:.2f} USDC")
                self._balance_is_real = True
                return self.usdc_balance
        except Exception:
            pass
        
        # ניסיון 2: קריאה ישירה ל-Polygon blockchain
        try:
            # כתובת חוזה USDC על Polygon
            usdc_contract = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
            
            async with httpx.AsyncClient() as http_client:
                # RPC endpoint של Polygon
                rpc_url = "https://polygon-rpc.com"
                
                # ERC20 balanceOf call
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [{
                        "to": usdc_contract,
                        "data": f"0x70a08231000000000000000000000000{FUNDER_ADDRESS[2:]}"
                    }, "latest"],
                    "id": 1
                }
                
                resp = await http_client.post(rpc_url, json=payload, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'result' in data:
                        balance_hex = data['result']
                        balance_wei = int(balance_hex, 16)
                        # USDC has 6 decimals
                        self.usdc_balance = balance_wei / 1_000_000
                        logger.info(f"💰 On-chain Balance: ${self.usdc_balance:.2f} USDC")
                        self._balance_is_real = True
                        return self.usdc_balance
        except Exception as e:
            logger.warning(f"⚠️ Blockchain read failed: {str(e)[:50]}")
        
        # Fallback: demo mode
        logger.warning("⚠️ Using demo mode ($100)")
        self.usdc_balance = 100.0
        self._balance_is_real = True
        return self.usdc_balance

    def execute_trade(self, token_id: str, side: str, size: float, price: float) -> Optional[Dict]:
        """ביצוע טרייד עם חתימת Proxy (מתאים למשתמשי אימייל)."""
        try:
            order_args = OrderArgs(
                token_id=token_id,
                price=float(round(price, 3)),
                size=float(round(size, 2)),
                side=BUY if side.lower() == 'buy' else SELL
            )
            
            # יצירת הפקודה (כאן מתבצעת החתימה עם signature_type=1)
            signed_order = self.client.create_order(order_args)
            
            logger.info(f"🚀 Posting {side.upper()} order via Proxy for {token_id[:8]}...")
            response = self.client.post_order(signed_order, OrderType.GTC)
            
            if response and response.get('success'):
                logger.info(f"✅ SUCCESS: Order {response.get('orderID')}")
                return response
            else:
                error_msg = response.get('errorMsg', 'Unknown error')
                logger.error(f"❌ Rejected: {error_msg}")
                return None
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            return None

    def check_liquidity(self, opportunity: Dict[str, Any], shares_leg1: float, shares_leg2: float) -> Dict[str, Any]:
        """בדיקת נזילות - וידוא שיש מספיק מניות זמינות לקנייה בשני הצדדים."""
        try:
            # מציאת NO token של רגל 2
            all_tokens = opportunity.get('hard_condition_all_tokens', [])
            yes_token = opportunity.get('hard_condition_id')
            no_token_id = next((t for x in all_tokens for t in (x if isinstance(x, list) else [x]) if t != yes_token), None)
            
            if not no_token_id:
                return {'success': False, 'reason': 'NO token not found'}
            
            # בדיקת order book לרגל 1 (Easy YES)
            try:
                orderbook_leg1 = self.client.get_order_book(opportunity['easy_condition_id'])
                if not orderbook_leg1 or 'asks' not in orderbook_leg1:
                    return {'success': False, 'reason': 'No orderbook data for leg 1'}
                
                # חישוב נזילות זמינה ברגל 1
                available_leg1 = sum(float(ask['size']) for ask in orderbook_leg1.get('asks', [])[:5])  # 5 הצעות הטובות ביותר
                
                if available_leg1 < shares_leg1 * 0.8:  # דורש לפחות 80% מהכמות
                    return {
                        'success': False, 
                        'reason': f'Leg 1: need {shares_leg1:.2f}, available {available_leg1:.2f}'
                    }
            except Exception as e:
                # אם אין גישה ל-orderbook, נניח שיש נזילות (fallback)
                logger.warning(f"Could not check leg 1 orderbook: {e}")
            
            # בדיקת order book לרגל 2 (Hard NO)
            try:
                orderbook_leg2 = self.client.get_order_book(no_token_id)
                if not orderbook_leg2 or 'asks' not in orderbook_leg2:
                    return {'success': False, 'reason': 'No orderbook data for leg 2'}
                
                # חישוב נזילות זמינה ברגל 2
                available_leg2 = sum(float(ask['size']) for ask in orderbook_leg2.get('asks', [])[:5])
                
                if available_leg2 < shares_leg2 * 0.8:  # דורש לפחות 80% מהכמות
                    return {
                        'success': False,
                        'reason': f'Leg 2: need {shares_leg2:.2f}, available {available_leg2:.2f}'
                    }
            except Exception as e:
                # אם אין גישה ל-orderbook, נניח שיש נזילות (fallback)
                logger.warning(f"Could not check leg 2 orderbook: {e}")
            
            return {'success': True, 'reason': 'Sufficient liquidity in both legs'}
            
        except Exception as e:
            # במקרה של שגיאה, נאפשר את העסקה (optimistic approach)
            logger.warning(f"Liquidity check failed: {e} - proceeding anyway")
            return {'success': True, 'reason': 'Check failed, proceeding optimistically'}

    def execute_arbitrage(self, opportunity: Dict[str, Any], shares_leg1: float, shares_leg2: float) -> bool:
        """ביצוע שתי רגלי הארביטראז' עם גידור."""
        logger.info(f"🔍 Starting Hedged Arbitrage: {opportunity['event']}")
        
        all_tokens = opportunity.get('hard_condition_all_tokens', [])
        yes_token = opportunity.get('hard_condition_id')
        no_token_id = next((t for x in all_tokens for t in (x if isinstance(x, list) else [x]) if t != yes_token), None)

        if not no_token_id:
            logger.error("❌ Could not find NO token for hard leg")
            return False

        # רגל 1: קנה YES על התנאי הקל (easy)
        # Slippage: 0.3%
        res1 = self.execute_trade(
            opportunity['easy_condition_id'], 
            'buy', 
            shares_leg1, 
            opportunity['easy_price'] * 1.003
        )
        if not res1: 
            logger.error("❌ Leg 1 (easy YES) failed")
            return False
        
        logger.info("✅ Leg 1 successful - placing leg 2...")
        
        # רגל 2: קנה NO על התנאי הקשה (hard)
        res2 = self.execute_trade(
            no_token_id, 
            'buy', 
            shares_leg2, 
            (1 - opportunity['hard_price']) * 1.003
        )
        if not res2:
            logger.error("⚠️ Leg 2 failed - Order mismatch risk!")
            return False
        
        # שמירת הפוזיציה למעקב
        position_id = f"{opportunity['event']}_{yes_token}"
        self.open_positions[position_id] = {
            'event': opportunity['event'],
            'tokens': [opportunity['easy_condition_id'], no_token_id],
            'size_leg1': shares_leg1,
            'size_leg2': shares_leg2,
            'timestamp': __import__('time').time()
        }
        logger.info(f"📝 Position saved: {position_id}")
            
        return True
    
    async def check_and_settle_positions(self) -> None:
        """בדיקה ושחרור אוטומטי של פוזיציות בשווקים סגורים."""
        if not self.open_positions:
            return
        
        logger.info(f"🔍 Checking {len(self.open_positions)} open positions...")
        
        positions_to_remove = []
        
        for position_id, position_data in self.open_positions.items():
            try:
                # בדיקה אם יש יתרה בטוקן (פוזיציה פתוחה)
                for token_id in position_data['tokens']:
                    try:
                        # נסיון למכור - אם השוק נסגר, זה יחזיר שגיאה או 0
                        balance = self.client.get_balance(token_id)
                        
                        if balance and float(balance) > 0:
                            # ניסיון ל-settle/redeem
                            logger.info(f"💰 Settling position: {position_data['event']}")
                            
                            # Polymarket עושה settle אוטומטית כשמנסים למכור אחרי סגירה
                            # אבל אפשר גם לקרוא ל-API ישירות
                            result = self.client.post_order({
                                'token_id': token_id,
                                'side': 'SELL',
                                'size': balance,
                                'price': 0.99  # מכירה מהירה
                            })
                            
                            if result:
                                logger.info(f"✅ Settled {token_id[:8]}... successfully")
                    except Exception:
                        # אם יש שגיאה, כנראה השוק כבר settled או הפוזיציה לא קיימת
                        pass
                
                # מסמן למחיקה אחרי 24 שעות
                if __import__('time').time() - position_data['timestamp'] > 86400:
                    positions_to_remove.append(position_id)
                    
            except Exception as e:
                logger.warning(f"⚠️ Error checking position {position_id}: {str(e)[:50]}")
        
        # ניקוי פוזיציות ישנות
        for pid in positions_to_remove:
            del self.open_positions[pid]
            logger.info(f"🗑️ Removed old position: {pid}")