#!/usr/bin/env python3
"""
Launcher script - workaround for terminal issues
This directly imports and runs the bot without terminal dependency
"""
import sys
import os

# Add the bot directory to path
bot_dir = r"C:\Users\shh92\OneDrive\Documenti\BotPolymarket\polymarket_bot"
if bot_dir not in sys.path:
    sys.path.insert(0, bot_dir)

# Change working directory
os.chdir(bot_dir)

# Now run the bot
if __name__ == "__main__":
    print("="*60)
    print("[LAUNCHER] Polymarket Arbitrage Bot")
    print("="*60)
    print(f"[INFO] Working directory: {os.getcwd()}")
    print(f"[INFO] Python version: {sys.version}")
    print()
    
    try:
        # Import and run main
        import asyncio
        from main import main
        
        print("[RUN] Starting bot...\n")
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Keyboard interrupt received")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
