# 🎯 Quick Start Guide

## What is this?
Automated bot that doubles money on Polymarket crypto markets.

## How does it work?
1. Finds markets at extreme prices (0.04$ or 0.996$)
2. Buys
3. Waits for price to double (0.08$ or 0.998$)
4. Sells at profit!

## Quick Start
1. `INSTALL.bat` - Install dependencies
2. Edit `config/.env` - Add your API keys
3. `TEST_SIMPLE_BOT.bat` - Test (no real trades)
4. `START_SIMPLE_BOT.bat` - Run the bot!

## Features
✅ Crypto markets only
✅ 8+ hours until close
✅ Entry: 0.01-0.10 or 0.992-0.996 (fractional cents)
✅ Exit: 2x price
✅ No stop loss

## Files
- `README.md` - Full documentation
- `run_simple_bot.py` - Main bot runner
- `test_simple_bot.py` - Test scanner only
- `src/polymarket_bot/` - Bot code

## Configuration
Edit `run_simple_bot.py`:
- `position_size_usd=10.0` - $ per trade
- `scan_interval_seconds=300` - Scan every 5 min
- `price_check_interval_seconds=30` - Check prices every 30 sec

## ⚠️ Warning
Real trading = Real risk! Start with small amounts ($5-10).

---
For full docs: [README.md](README.md)
