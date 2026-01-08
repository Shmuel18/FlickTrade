# run_simple_bot.py
"""
הרצה פשוטה של הבוט
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from polymarket_bot.simple_bot import main
from polymarket_bot.config import BUY_PRICE_THRESHOLD, SELL_MULTIPLIER, PORTFOLIO_PERCENT, MIN_POSITION_USD

if __name__ == "__main__":
    print("🚀 Starting Simple Crypto Bot...")
    print("=" * 60)
    print("Strategy:")
    print("  • Scan ALL markets with extreme low prices")
    print(f"  • Buy at: ≤ ${BUY_PRICE_THRESHOLD} ({BUY_PRICE_THRESHOLD*100:.1f} cents)")
    print(f"  • Sell at: {SELL_MULTIPLIER}x price (${BUY_PRICE_THRESHOLD * SELL_MULTIPLIER})")
    print(f"  • Position size: {PORTFOLIO_PERCENT*100}% of portfolio (min ${MIN_POSITION_USD})")
    print("  • NO stop loss - hold until target")
    print("  • Only markets with 1+ hours until close")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
