#!/usr/bin/env python3
"""
Polymarket Arbitrage Bot - Main Entry Point
Professional launcher for the trading bot with optimized logging
"""

import sys
import os
import asyncio
from pathlib import Path

# Get project root
project_root = Path(__file__).parent
src_path = str(project_root / 'src')

# Add src to Python path
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Set environment variables for paths
os.environ['BOT_ROOT'] = str(project_root)
os.environ['BOT_CONFIG_DIR'] = str(project_root / 'config')
os.environ['BOT_LOG_DIR'] = str(project_root / 'logs')

# Import and run bot
try:
    from polymarket_bot.main import main
    if __name__ == '__main__':
        print("\n" + "="*70)
        print("  🤖 POLYMARKET ARBITRAGE BOT - OPTIMIZED MODE")
        print("="*70)
        print("  ✅ Reduced logging to prevent system overload")
        print("  ✅ Log rotation enabled (max 20MB total)")
        print("  ✅ Only INFO and higher messages shown")
        print("="*70 + "\n")
        asyncio.run(main())
except KeyboardInterrupt:
    print("\n✋ Bot stopped by user")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
