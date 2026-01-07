# PERSISTENCE & ANALYTICS

## Transaction CSV Logging

All executed arbitrage trades are automatically logged to:

```
logs/transactions.csv
```

### CSV Columns:

- `timestamp` - When the trade was executed
- `event_title` - Market event name
- `easy_condition_id` - Parent/easy condition token
- `hard_condition_id` - Child/hard condition token
- `easy_price` - Entry price for easy condition
- `hard_price` - Entry price for hard condition
- `profit_margin_pct` - Expected profit percentage
- `order_size` - Number of shares traded
- `usdc_invested` - Total USDC deployed
- `leg1_order_id` - Buy order ID for easy condition
- `leg2_order_id` - Buy order ID for NO on hard condition
- `leg1_status` - Status of leg 1 (pending/confirmed)
- `leg2_status` - Status of leg 2 (pending/confirmed)
- `transaction_id` - Unique transaction identifier

## Performance Monitoring

The bot generates performance reports at shutdown showing:

### Session Statistics:

- Duration in hours
- Total price updates received
- Total opportunities detected
- Trades attempted & successful
- Session P&L (Profit & Loss)

### Historical Statistics (from CSV):

- Total transactions executed
- Success rate percentage
- Estimated cumulative profit
- Average profit per trade

### Accessing Reports:

Reports are logged to console at:

1. **Every 5 minutes** - Interim stats
2. **On shutdown** - Comprehensive performance report

## Analysis Tools

To analyze historical performance:

```python
from polymarket_bot.persistence import TransactionLogger

logger = TransactionLogger()
stats = logger.get_statistics()
print(f"Success Rate: {stats['success_rate_pct']:.1f}%")
print(f"Total Profit: ${stats['estimated_total_profit']:.2f}")
```

## Future Enhancements

### 1. Async CLOB Client

Currently uses `py_clob_client` with `asyncio.to_thread` wrapper.
Future: Replace with fully async HTTP library (aiohttp) for better resource efficiency.

### 2. SQLite Database

Could migrate from CSV to SQLite for:

- Better query performance
- Complex filtering and sorting
- Real-time analytics dashboards

### 3. Alert Notifications

Could add:

- Email alerts for large trades
- Slack notifications for errors
- Webhook integration for external monitoring
