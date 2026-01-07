# test_get_price.py
"""בודק את הפונקציה get_current_price"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from polymarket_bot.simple_scanner import get_current_price

token_id = "93592949212798121127213117304912625505836768562433217537850469496310204567695"

print(f"🔍 בודק מחיר עבור token: {token_id[:20]}...")
price = get_current_price(token_id)

if price:
    print(f"✅ מחיר: ${price:.4f}")
else:
    print("❌ לא הצלחתי לקבל מחיר")
