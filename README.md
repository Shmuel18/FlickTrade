# 🤖 Simple Crypto Bot - Polymarket

Simple and effective bot for doubling investments in Polymarket crypto markets.

## 🎯 Strategy

The bot looks for markets with **extreme prices** (fractional cents) and tries to double the investment:

1. **Scan**: Finds crypto markets with extreme prices (0.04$ or 0.996$)
2. **Entry**: Buys at extreme price
3. **Target**: Sells when price doubles (0.08$ or 0.998$)
4. **No Stop Loss**: Holds position until target is reached

### Example (Low Price)

- Buy: 250 shares @ $0.04 = $10
- Sell: 250 shares @ $0.08 = $20
- Profit: **$10 (100%)**

### Example (High Price)

- Buy: 250 shares @ $0.996 = $249
- Sell: 250 shares @ $0.998 = $249.50
- Profit: **$0.50 per cycle**

## ✅ Market Requirements

The bot only trades markets that meet:

- ✅ Crypto category (Bitcoin, Ethereum, etc.)
- ✅ At least **8 hours** until market closes
- ✅ Price: 0.01-0.10 or 0.990-0.999 (fractional cents only)

## 📦 Installation

1. Make sure you have Python 3.8+
2. Install requirements:

```bash
pip install -r config/requirements.txt
```

Or double-click: `INSTALL.bat`

3. Configure API keys in `config/.env`:

```
POLYMARKET_API_KEY=your_key_here
POLYMARKET_API_SECRET=your_secret_here
POLYMARKET_API_PASSPHRASE=your_passphrase_here
POLYMARKET_PRIVATE_KEY=your_private_key_here
POLYMARKET_FUNDER_ADDRESS=your_wallet_address_here
```

## 🚀 Usage

### Test (No Real Trading)

```bash
python test_simple_bot.py
```

Or: `TEST_SIMPLE_BOT.bat`

### Run Bot

```bash
python run_simple_bot.py
```

Or: `START_SIMPLE_BOT.bat`

### Configuration

Edit `run_simple_bot.py` to customize:

```python
bot = SimpleCryptoBot(
    position_size_usd=10.0,           # $ per trade
    scan_interval_seconds=300,        # Scan every 5 minutes
    price_check_interval_seconds=30   # Check prices every 30 seconds
)
```

## 📊 What the Bot Does

### Scan Loop (Every 5 minutes)

1. Searches Polymarket for crypto markets
2. Filters by extreme price (0.01-0.10 or 0.92-0.99)
3. Filters by time (8+ hours until close)
4. Enters new positions if budget available

### Monitor Loop (Every 30 seconds)

1. Checks prices of open positions
2. Exits when price doubles ✅
3. Holds otherwise (no stop loss)

## 📈 Example Output

```
🚀 SimpleCryptoBot STARTED
💵 Balance: $100.00 USDC

============================================================
🔍 Scan #1 - 14:23:45
============================================================
📊 Found 500 active events
✅ Found: Bitcoin above $100k by Jan 15? | YES @ $0.0423 | Target: $0.0846 | 12.5h
✅ Found: ETH below $3000? | NO @ $0.9689 | Target: $0.9844 | 9.2h
🎯 Total: 2 opportunities

🎯 Entering trade: Bitcoin above $100k by Jan 15?
   YES @ $0.0423 | 236 shares
✅ Entered @ $0.0423 | Target: $0.0846

📊 Statistics:
   Scans: 1
   Opportunities found: 2
   Positions opened: 1
   Positions closed: 0

📊 1 open positions:
  • Bitcoin above $100k by Jan 15?
    Entry: $0.0423 | Target: $0.0846

⏳ Waiting 300 seconds until next scan...

[After some time...]

🎉 Target reached! $0.0423 → $0.0852
💰 Exited: TARGET_REACHED
   P&L: $10.12 (+100.2%)
```

## ⚙️ Main Files

- **`simple_bot.py`** - Main bot, orchestrates everything
- **`simple_scanner.py`** - Scans Polymarket markets
- **`simple_trader.py`** - Manages entry/exit logic
- **`executor.py`** - Executes buy/sell orders
- **`config.py`** - Configuration and API keys

## 🛡️ Risk Management

The bot includes:

- ✅ Balance check before each trade
- ✅ Prevents duplicate entries to same market
- ✅ Continuous monitoring of open positions
- ❌ No stop loss - holds until target

## ⚠️ Warning

- This is real automated trading - you can lose money!
- Start with small amounts ($5-10 per trade)
- Bot is still in development - use carefully
- Crypto markets are especially volatile

## 🔧 Troubleshooting

### "No opportunities found"

- Normal! Not always markets with extreme prices exist
- Bot will keep scanning automatically

### "Balance too low"

- Make sure you have enough USDC in wallet
- Reduce `position_size_usd`

### "API errors"

- Check that API keys are correct in `.env` file
- Verify wallet is properly connected

---

**Good luck! 🚀💰**
