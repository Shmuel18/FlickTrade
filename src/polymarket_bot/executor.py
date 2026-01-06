# executor.py
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from .config import (
    CLOB_URL, API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY, 
    CHAIN_ID, MAX_USDC_ALLOCATION
)

logger = logging.getLogger(__name__)

@dataclass
class Order:
    """Represents a placed order."""
    order_id: str
    token_id: str
    side: str
    size: float
    price: float
    status: str
    timestamp: datetime
    
class OrderExecutor:
    """Handles order execution for Polymarket arbitrage trades."""
    
    def __init__(self):
        """Initialize OrderExecutor with API credentials."""
        try:
            # Validate credentials
            if not all([API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY]):
                raise ValueError("Missing required API credentials")
            
            # Create credentials object
            creds = ApiCreds(
                api_key=API_KEY,
                api_secret=API_SECRET,
                api_passphrase=API_PASSPHRASE
            )
            
            # Initialize CLOB client
            self.client = ClobClient(
                host=CLOB_URL,
                key=PRIVATE_KEY,
                chain_id=CHAIN_ID,
                creds=creds
            )
            
            self.orders: Dict[str, Order] = {}
            logger.info("✅ OrderExecutor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OrderExecutor: {e}")
            raise

    def execute_trade(self, clob_token_id: str, side: str, size: float, 
                      price: float, order_type: str = 'limit') -> Optional[Dict[str, Any]]:
        """Execute a single limit order.
        
        Args:
            clob_token_id: Token ID to trade
            side: 'buy' or 'sell'
            size: Number of shares to trade
            price: Limit price (0-1 for yes/no tokens)
            order_type: Order type ('limit' or 'market')
        
        Returns:
            Order details if successful, None if failed
        """
        try:
            # Validate inputs
            if side not in ['buy', 'sell']:
                logger.error(f"Invalid side: {side}")
                return None
            
            if not (0 < price <= 1):
                logger.warning(f"Price {price} outside valid range (0, 1]")
                return None
            
            if size <= 0:
                logger.error(f"Invalid size: {size}")
                return None
            
            logger.info(f"Executing order: {side} {size} shares of {clob_token_id[:10]}... @ ${price}")
            
            # Create and submit order
            response = self.client.create_order(
                clob_token_id=clob_token_id,
                side=side,
                size=size,
                price=price,
                order_type=order_type
            )
            
            if response:
                order_id = response.get('id', response.get('orderId'))
                if order_id:
                    # Store order record
                    order = Order(
                        order_id=order_id,
                        token_id=clob_token_id,
                        side=side,
                        size=size,
                        price=price,
                        status='pending',
                        timestamp=datetime.now()
                    )
                    self.orders[order_id] = order
                    logger.info(f"✅ Order placed: {order_id}")
                    return response
            else:
                logger.error("Order response is empty")
                return None
                
        except Exception as e:
            logger.error(f"Trade execution failed for {clob_token_id}: {e}")
            return None
    
    def execute_arbitrage(self, opportunity: Dict[str, Any], order_size: float) -> bool:
        """Execute both legs of an arbitrage trade.
        
        Args:
            opportunity: Arbitrage opportunity dict from logic.check_arbitrage
            order_size: Size of each leg (same for both)
        
        Returns:
            True if both orders placed successfully
        """
        try:
            logger.info(f"Executing arbitrage: {opportunity['event']}")
            
            # Leg 1: Buy the hard condition (cheaper)
            leg1 = self.execute_trade(
                clob_token_id=opportunity['hard_condition_id'],
                side='buy',
                size=order_size,
                price=opportunity['hard_price'],
                order_type='limit'
            )
            
            if not leg1:
                logger.error("Failed to execute leg 1 (buy hard condition)")
                return False
            
            # Leg 2: Sell the easy condition (expensive)
            leg2 = self.execute_trade(
                clob_token_id=opportunity['easy_condition_id'],
                side='sell',
                size=order_size,
                price=opportunity['easy_price'],
                order_type='limit'
            )
            
            if not leg2:
                logger.error("Failed to execute leg 2 (sell easy condition)")
                return False
            
            logger.info(f"✅ Arbitrage executed successfully - Profit: ${opportunity['profit_margin'] * order_size:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Arbitrage execution failed: {e}")
            return False
    
    def get_order_status(self, order_id: str) -> Optional[str]:
        """Get status of a previously placed order.
        
        Args:
            order_id: Order ID to check
        
        Returns:
            Order status or None if not found
        """
        try:
            if order_id not in self.orders:
                return None
            return self.orders[order_id].status
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return None