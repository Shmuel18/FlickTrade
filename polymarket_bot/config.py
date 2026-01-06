# config.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API Configuration
API_KEY = os.getenv("POLYMARKET_API_KEY")
API_SECRET = os.getenv("POLYMARKET_API_SECRET")
API_PASSPHRASE = os.getenv("POLYMARKET_API_PASSPHRASE")
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")

# Validate required credentials
required_env_vars = ["POLYMARKET_API_KEY", "POLYMARKET_API_SECRET", 
                     "POLYMARKET_API_PASSPHRASE", "POLYMARKET_PRIVATE_KEY"]
for var in required_env_vars:
    if not os.getenv(var):
        logging.warning(f"Missing environment variable: {var}")

# API URLs
GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
CLOB_WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

# Blockchain Configuration
CHAIN_ID = 137  # Polygon (MATIC)

# Trading Configuration
PROFIT_THRESHOLD = 0.02  # 2% minimum profit threshold
MAX_USDC_ALLOCATION = 0.05  # Max 5% of balance per trade
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
WS_PING_INTERVAL = 20
WS_PING_TIMEOUT = 20
API_RATE_LIMIT_DELAY = 1  # seconds between API calls
MARKET_SCAN_INTERVAL = 3600  # 1 hour in seconds

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('polymarket_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)