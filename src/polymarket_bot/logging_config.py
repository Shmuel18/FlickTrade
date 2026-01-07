# logging_config.py
"""
Optimized logging configuration to prevent system overload
"""
import logging
import logging.handlers
from pathlib import Path
import os

def setup_logging():
    """
    Configure logging with rotation and reduced verbosity to prevent crashes.
    
    Key improvements:
    - Log rotation to prevent unlimited file growth
    - Reduced console output (INFO level only)
    - File logging with size limits
    - Minimal DEBUG logs
    """
    
    # Get log directory
    log_dir = Path(os.environ.get('BOT_LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True)
    
    # Main log file with rotation (max 5MB per file, keep 3 backups)
    log_file = log_dir / 'bot.log'
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Root logger - set to WARNING by default (most restrictive)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler - INFO level only (not DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler with rotation - INFO level
    # Max 5MB per file, keep 3 backup files = max 20MB total
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Set specific loggers to appropriate levels
    # Our bot modules - INFO level (no DEBUG)
    logging.getLogger('polymarket_bot').setLevel(logging.INFO)
    logging.getLogger('polymarket_bot.main').setLevel(logging.INFO)
    logging.getLogger('polymarket_bot.scanner').setLevel(logging.INFO)
    logging.getLogger('polymarket_bot.ws_manager').setLevel(logging.INFO)
    logging.getLogger('polymarket_bot.executor').setLevel(logging.INFO)
    logging.getLogger('polymarket_bot.logic').setLevel(logging.INFO)
    logging.getLogger('polymarket_bot.persistence').setLevel(logging.INFO)
    
    # External libraries - WARNING or ERROR only
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    logging.info("="*60)
    logging.info("Logging system initialized (Optimized Mode)")
    logging.info(f"Log file: {log_file}")
    logging.info(f"Console level: INFO | File level: INFO")
    logging.info(f"Max log size: 5MB per file, 3 backups (20MB total)")
    logging.info("="*60)
