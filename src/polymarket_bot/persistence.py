# persistence.py
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TransactionLogger:
    """Log arbitrage transactions to CSV for analysis and record-keeping."""
    
    def __init__(self, log_dir: Path = None):
        """Initialize transaction logger.
        
        Args:
            log_dir: Directory to store transaction CSV
        """
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_path = self.log_dir / "transactions.csv"
        self.csv_headers = [
            'timestamp',
            'event_title',
            'easy_condition_id',
            'hard_condition_id',
            'easy_price',
            'hard_price',
            'profit_margin_pct',
            'order_size',
            'usdc_invested',
            'leg1_order_id',
            'leg2_order_id',
            'leg1_status',
            'leg2_status',
            'transaction_id'
        ]
        
        # Initialize CSV file if it doesn't exist
        if not self.csv_path.exists():
            self._create_csv_file()
    
    def _create_csv_file(self) -> None:
        """Create CSV file with headers."""
        try:
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()
        except Exception as e:
            logger.error(f"Failed to create CSV file: {e}")
    
    def log_transaction(self, transaction: Any, opportunity: Dict[str, Any]) -> None:
        """Log a completed transaction to CSV.
        
        Args:
            transaction: ArbitrageTransaction object
            opportunity: Original opportunity dict that triggered the trade
        """
        try:
            row = {
                'timestamp': datetime.now().isoformat(),
                'event_title': opportunity.get('event', 'Unknown'),
                'easy_condition_id': opportunity.get('easy_condition_id', ''),
                'hard_condition_id': opportunity.get('hard_condition_id', ''),
                'easy_price': f"{opportunity.get('easy_price', 0):.4f}",
                'hard_price': f"{opportunity.get('hard_price', 0):.4f}",
                'profit_margin_pct': f"{opportunity.get('profit_pct', 0):.2f}",
                'order_size': f"{transaction.order_size:.2f}",
                'usdc_invested': f"{transaction.usdc_invested:.2f}",
                'leg1_order_id': transaction.leg1_order_id or 'N/A',
                'leg2_order_id': transaction.leg2_order_id or 'N/A',
                'leg1_status': transaction.leg1_status,
                'leg2_status': transaction.leg2_status,
                'transaction_id': transaction.transaction_id
            }
            
            with open(self.csv_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writerow(row)
            
        except Exception as e:
            logger.error(f"Failed to log transaction: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Read CSV and calculate performance statistics.
        
        Returns:
            Dictionary with stats
        """
        try:
            if not self.csv_path.exists():
                return {}
            
            transactions = []
            with open(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('transaction_id'):  # Skip header and empty rows
                        transactions.append(row)
            
            if not transactions:
                return {}
            
            # Calculate stats
            successful = sum(1 for t in transactions 
                            if t.get('leg1_status') == 'confirmed' and t.get('leg2_status') == 'confirmed')
            
            total_profit = sum(
                float(t.get('profit_margin_pct', 0)) * float(t.get('order_size', 0))
                for t in transactions
                if t.get('leg1_status') == 'confirmed'
            )
            
            return {
                'total_transactions': len(transactions),
                'successful': successful,
                'failed': len(transactions) - successful,
                'success_rate_pct': (successful / len(transactions) * 100) if transactions else 0,
                'estimated_total_profit': total_profit,
                'avg_profit_per_trade': total_profit / successful if successful > 0 else 0,
                'csv_path': str(self.csv_path)
            }
        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            return {}


class PerformanceMonitor:
    """Monitor and report bot performance."""
    
    def __init__(self, transaction_logger: TransactionLogger = None):
        """Initialize performance monitor.
        
        Args:
            transaction_logger: TransactionLogger instance
        """
        self.transaction_logger = transaction_logger
        self.session_stats = {
            'start_time': datetime.now(),
            'price_updates': 0,
            'opportunities_found': 0,
            'trades_attempted': 0,
            'trades_successful': 0,
            'total_pnl': 0.0
        }
    
    def report(self) -> None:
        """Report current session and historical statistics."""
        try:
            elapsed = (datetime.now() - self.session_stats['start_time']).total_seconds()
            hours = elapsed / 3600
            
            logger.info("\n" + "="*70)
            logger.info("📊 PERFORMANCE REPORT")
            logger.info("="*70)
            
            # Session stats
            logger.info(f"⏱️  Session Duration: {hours:.2f} hours")
            logger.info(f"📈 Price Updates: {self.session_stats['price_updates']}")
            logger.info(f"🔍 Opportunities Found: {self.session_stats['opportunities_found']}")
            logger.info(f"💼 Trades Attempted: {self.session_stats['trades_attempted']}")
            logger.info(f"✅ Trades Successful: {self.session_stats['trades_successful']}")
            logger.info(f"💰 Session P&L: ${self.session_stats['total_pnl']:.2f}")
            
            # Historical stats from CSV
            if self.transaction_logger:
                stats = self.transaction_logger.get_statistics()
                if stats:
                    logger.info("\n" + "-"*70)
                    logger.info("📁 HISTORICAL PERFORMANCE (from CSV)")
                    logger.info("-"*70)
                    logger.info(f"Total Transactions: {stats.get('total_transactions', 0)}")
                    logger.info(f"Successful: {stats.get('successful', 0)}")
                    logger.info(f"Failed: {stats.get('failed', 0)}")
                    logger.info(f"Success Rate: {stats.get('success_rate_pct', 0):.1f}%")
                    logger.info(f"Estimated Total Profit: ${stats.get('estimated_total_profit', 0):.2f}")
                    logger.info(f"Average Per Trade: ${stats.get('avg_profit_per_trade', 0):.4f}")
                    logger.info(f"CSV Path: {stats.get('csv_path', 'N/A')}")
            
            logger.info("="*70 + "\n")
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
