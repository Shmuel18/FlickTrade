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

if __name__ == "__main__":
    print("🚀 Starting Simple Crypto Bot...")
    print("=" * 60)
    print("Strategy:")
    print("  • Scan crypto markets with extreme low prices")
    print("  • Buy at: ≤ 0.004 (0.4 cents)")
    print("  • Sell at: 2x price (0.008 = 0.8 cents)")
    print("  • NO stop loss - hold until target")
    print("  • Only markets with 8+ hours until close")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
