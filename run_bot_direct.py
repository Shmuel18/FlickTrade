#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to bot directory
bot_dir = r"C:\Users\shh92\OneDrive\Documenti\BotPolymarket\polymarket_bot"
os.chdir(bot_dir)

# Run the bot
subprocess.run([sys.executable, "main.py"])
