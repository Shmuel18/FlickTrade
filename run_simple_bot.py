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
    print("  • Scan crypto markets with extreme prices")
    print("  • Low: 0.01-0.10 (buy 0.04, sell 0.08)")
    print("  • High: 0.992-0.996 (buy 0.996, sell 0.998)")
    print("  • Exit at 2x price")
    print("  • NO stop loss - hold until target")
    print("  • Only markets with 8+ hours until close")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
