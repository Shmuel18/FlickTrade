# config.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / "config" / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# API Configuration
API_KEY = os.getenv("POLYMARKET_API_KEY")
API_SECRET = os.getenv("POLYMARKET_API_SECRET")
API_PASSPHRASE = os.getenv("POLYMARKET_API_PASSPHRASE")
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")
FUNDER_ADDRESS = os.getenv("POLYMARKET_FUNDER_ADDRESS")

# Validate required credentials
required_env_vars = ["POLYMARKET_API_KEY", "POLYMARKET_API_SECRET", 
                     "POLYMARKET_API_PASSPHRASE", "POLYMARKET_PRIVATE_KEY", 
                     "POLYMARKET_FUNDER_ADDRESS"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    error_msg = f"CRITICAL: Missing required environment variables: {', '.join(missing_vars)}"
    raise EnvironmentError(error_msg)

# API URLs
GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
CLOB_WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

# Blockchain Configuration
CHAIN_ID = 137  # Polygon (MATIC)

# Trading Configuration
PROFIT_THRESHOLD = 0.02
MAX_USDC_ALLOCATION = 0.05
SLIPPAGE_TOLERANCE = 0.01
MIN_LIQUIDITY = 100
STOP_LOSS_PERCENT = 0.05
MAX_RETRIES = 3
RETRY_DELAY = 2

# Strategy Configuration (Single Source of Truth)
BUY_PRICE_THRESHOLD = 0.004  # Maximum price to buy ($0.004 = 0.4 cents)
SELL_MULTIPLIER = 2.0        # Sell at 2x entry price ($0.008 = 0.8 cents)
PORTFOLIO_PERCENT = 0.005    # 0.5% of portfolio per trade
MIN_POSITION_USD = 1.0       # Minimum $1 per trade
WS_PING_INTERVAL = 20
WS_PING_TIMEOUT = 20
API_RATE_LIMIT_DELAY = 1
MARKET_SCAN_INTERVAL = 3600
ORDER_TIMEOUT = 30

logger = logging.getLogger(__name__)