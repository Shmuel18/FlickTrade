# Polymarket Arbitrage Bot - Project Structure

## Overview

Professional-grade automated trading bot for identifying and executing arbitrage opportunities on Polymarket.

## Directory Structure

```
BotPolymarket/
├── src/                              # Source code
│   ├── polymarket_bot/              # Main bot package
│   │   ├── main.py                  # Bot orchestrator & async task manager
│   │   ├── scanner.py               # Gamma API market scanner
│   │   ├── ws_manager.py            # CLOB WebSocket connection manager
│   │   ├── logic.py                 # Arbitrage detection engine
│   │   ├── executor.py              # Order execution & tracking
│   │   └── config.py                # Logging setup & configuration
│   │
│   └── utils/                       # Utility scripts
│       ├── debug_api.py             # API response analyzer
│       └── debug_markets.py         # Market data debugger
│
├── scripts/                          # Launch & deployment scripts
│   ├── run_bot.py                   # Python launcher
│   ├── run_bot.bat                  # Windows batch launcher
│   ├── launcher.py                  # Enhanced Python launcher
│   ├── run_bot.ps1                  # PowerShell launcher
│   ├── run_bot_direct.py            # Direct execution
│   ├── start_bot.bat                # Simple batch launcher
│   └── Run Bot.url                  # Windows desktop shortcut
│
├── config/                           # Configuration files
│   ├── .env                         # API credentials (NEVER commit)
│   └── requirements.txt             # Python dependencies
│
├── logs/                             # Runtime logs
│   └── polymarket_bot.log           # Application logs
│
├── git/                              # Version control utilities
│   ├── push_to_git.py               # Git commit & push script
│   ├── push_to_git.bat              # Batch git pusher
│   └── upload_to_git.py             # GitHub uploader
│
├── docs/                             # Documentation
│   ├── README.md                    # Main documentation
│   └── PROJECT_STRUCTURE.md         # This file
│
├── run_bot.py                        # Root launcher (runs from project root)
├── run_bot.bat                       # Root Windows launcher
├── .gitignore                        # Git ignore rules
└── .git/                             # Git repository

```

## File Descriptions

### Core Bot Modules (src/polymarket_bot/)

**main.py**

- Entry point for the bot
- `PolymarketBot` class: Main orchestrator
- Manages: WebSocket connection, market scanning, price monitoring, order execution
- Handles: Signal processing, graceful shutdown, statistics reporting

**scanner.py**

- Queries Gamma API for events and markets
- Identifies hierarchical market structures (events with 2+ markets)
- Returns: Market data with token IDs and metadata

**ws_manager.py**

- Manages WebSocket connection to CLOB (Central Limit Order Book)
- Handles: Connection, subscription, price updates, reconnection
- Provides: Async price stream with exponential backoff

**logic.py**

- Detects arbitrage opportunities from price discrepancies
- Compares parent/child market relationships
- Returns: Sorted list of opportunities by profit margin

**executor.py**

- Executes trades via CLOB protocol
- `OrderExecutor` class: Interface to py-clob-client
- Supports: Single orders, atomic dual-leg arbitrage execution
- Tracks: Order status, fills, rejections

**config.py**

- Logging configuration (file + console output)
- Environment variable management
- Trading parameters:
  - `PROFIT_THRESHOLD`: 2% minimum arbitrage spread
  - `MAX_USDC_ALLOCATION`: 5% max allocation per trade
  - `MARKET_SCAN_INTERVAL`: 1 hour between rescans

### Utility Scripts (src/utils/)

**debug_api.py**

- Analyzes Gamma API responses
- Shows: Event count, market groupings, token IDs

**debug_markets.py**

- Detailed market structure analysis
- Identifies: Hierarchical markets, their relationships, pricing

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r config/requirements.txt

# Configure credentials
# Edit config/.env with your Polymarket API keys
```

### 2. Run Bot

**Option A: From root (recommended)**

```bash
python run_bot.py
```

**Option B: Windows batch**

```bash
run_bot.bat
```

**Option C: PowerShell**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_bot.ps1
```

### 3. Monitor

Watch `logs/polymarket_bot.log` for:

- Market discovery: `[OK] Found X pairs from Y hierarchical markets`
- WebSocket connection: `[CONNECT] Connected to CLOB WebSocket`
- Price updates: `[STATS] Updates: X | Opportunities: Y`
- Arbitrage signals: `[ARBITRAGE] Event Name | Profit: $X.XX (Y%)`

## Configuration

### Environment Variables (.env)

```
API_KEY=your_api_key
API_SECRET=your_api_secret
API_PASSPHRASE=your_passphrase
PRIVATE_KEY=your_private_key
```

### Trading Parameters (src/polymarket_bot/config.py)

- `PROFIT_THRESHOLD = 0.02` (2% minimum spread)
- `MAX_USDC_ALLOCATION = 0.05` (5% max per trade)
- `MARKET_SCAN_INTERVAL = 3600` (1 hour rescan)

## Architecture

### Task Flow

1. **Scanner** → Discovers hierarchical markets from Gamma API
2. **WebSocket** → Subscribes to token prices via CLOB
3. **Logic** → Detects arbitrage opportunities as prices update
4. **Executor** → Places orders if profit threshold met
5. **Monitor** → Tracks orders, logs statistics

### Async Design

- All I/O operations (API, WebSocket, orders) are async
- Concurrent tasks: Scanning, monitoring, statistics reporting
- Graceful shutdown with signal handling

## API Connections

### Gamma API

- **Endpoint**: `https://gamma-api.polymarket.com/events`
- **Purpose**: Market discovery & metadata
- **Rate Limit**: Handled with request backoff

### CLOB WebSocket

- **Endpoint**: `wss://ws-subscriptions-clob.polymarket.com/ws/market`
- **Purpose**: Real-time price updates
- **Features**: Batch subscription, reconnection, exponential backoff

### CLOB REST

- **Purpose**: Order placement via py-clob-client
- **Auth**: API Key + Secret + Passphrase + Private Key

## Logs

All activity logged to `logs/polymarket_bot.log`:

- **INFO**: Market discovery, WebSocket events, statistics
- **WARNING**: Connection issues, missed opportunities
- **ERROR**: API failures, execution errors, critical issues

## Git Management

Push code to GitHub:

```bash
python git/push_to_git.py
```

Or use batch file:

```bash
git/push_to_git.bat
```

## Development

### Adding Features

1. Create new module in `src/polymarket_bot/`
2. Update imports in `main.py`
3. Add async method to `PolymarketBot` class
4. Test with: `python run_bot.py`

### Testing

Run diagnostic scripts:

```bash
python -c "import sys; sys.path.insert(0, 'src'); from utils.debug_api import *; analyze_markets()"
```

## Troubleshooting

**Bot finds 0 markets**

- Check API connectivity
- Verify Gamma API endpoint is accessible
- Run `python -c "import sys; sys.path.insert(0, 'src'); from utils.debug_markets import *"`

**WebSocket disconnects**

- Normal behavior - auto-reconnects with exponential backoff
- Check network stability
- Review logs for specific error messages

**Orders not executing**

- Verify API credentials in `.env`
- Check account has sufficient USDC
- Review executor.py for order validation

## Performance

- **Market Scan**: ~3 seconds for 500 events
- **Token Subscription**: ~5 seconds for 8000+ tokens
- **Price Update Latency**: <100ms
- **Arbitrage Detection**: <1ms per price update

## Security

- API credentials stored in `.env` (NEVER commit)
- Private key handled carefully by executor
- Orders signed on client side via py-clob-client
- No sensitive data logged

## Deployment

For production:

1. Run on stable server with 24/7 uptime
2. Use process manager (supervisor, systemd)
3. Monitor logs regularly
4. Set up alerts for errors
5. Periodically review and update trading parameters

## Support

For issues or questions:

1. Check logs for error messages
2. Run diagnostic utilities in `src/utils/`
3. Review configuration in `config/`
4. Check GitHub repository for updates
