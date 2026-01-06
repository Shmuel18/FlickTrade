#!/usr/bin/env python3
"""
Direct bot runner - no terminal dependencies
"""
import subprocess
import sys
import os

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# The bot directory
bot_dir = os.path.join(script_dir, "polymarket_bot")

print("="*70)
print("POLYMARKET ARBITRAGE BOT - DIRECT LAUNCHER")
print("="*70)
print(f"Script Location: {script_dir}")
print(f"Bot Location: {bot_dir}")
print(f"Python Executable: {sys.executable}")
print()

try:
    # Change to bot directory
    os.chdir(bot_dir)
    print(f"[INFO] Changed to: {os.getcwd()}")
    print()
    
    # Run the main script
    print("[RUN] Starting bot...\n")
    result = subprocess.run([sys.executable, "main.py"], check=False)
    
    if result.returncode == 0:
        print("\n[SUCCESS] Bot completed normally")
    else:
        print(f"\n[ERROR] Bot exited with code {result.returncode}")
        
except Exception as e:
    print(f"[FATAL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
