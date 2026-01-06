# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# מפתחות API - וודא שהם קיימים ב-.env שלך
API_KEY = os.getenv("POLYMARKET_API_KEY")
API_SECRET = os.getenv("POLYMARKET_API_SECRET")
API_PASSPHRASE = os.getenv("POLYMARKET_API_PASSPHRASE")
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY") # מפתח פרטי של הארנק

# כתובות שרתים
GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"
CLOB_WS_URL = "wss://clob.polymarket.com"
CHAIN_ID = 137  # Polygon Mainnet

# הגדרות מסחר
PROFIT_THRESHOLD = 0.02  # סף רווח של 2%
MAX_USDC_ALLOCATION = 0.05  # 5% מהיתרה לכל טרייד