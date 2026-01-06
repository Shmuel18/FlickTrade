import subprocess
import sys
import os

os.chdir(r'c:\Users\shh92\OneDrive\Documenti\BotPolymarket')

print("Starting Polymarket Arbitrage Bot...")
print("=" * 60)

result = subprocess.run([sys.executable, 'run_bot.py'])
sys.exit(result.returncode)
