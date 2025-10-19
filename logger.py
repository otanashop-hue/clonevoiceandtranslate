"""
Advanced logging system for the trading signal scanner
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from config_manager import ConfigManager


class TradingLogger:
    """
    Advanced logging system for trading signals and system events
    """
    
    def __init__(self, config_manager: ConfigManager = None):
        self.config_manager = config_manager or ConfigManager()
        self.logging_config = self.config_manager.get_logging_settings()
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Setup main logger
        self._setup_main_logger()
        
        # Setup signal logger
        self._setup_signal_logger()
        
        # Setup error logger
        self._setup_error_logger()
        
        # Setup performance logger
        self._setup_performance_logger()
    
    def _setup_main_logger(self):
        """Setup main application logger"""
        logger = logging.getLogger('trading_main')
        logger.setLevel(getattr(logging, self.logging_config.get('level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = os.path.join('logs', 'main.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.logging_config.get('max_log_size_mb', 10) * 1024 * 1024,
            backupCount=self.logging_config.get('backup_count', 5)
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        self.loggers['main'] = logger
    
    def _setup_signal_logger(self):
        """Setup signal-specific logger"""
        logger = logging.getLogger('trading_signals')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Signal file handler
        signal_file = os.path.join('logs', 'signals.log')
        signal_handler = logging.handlers.RotatingFileHandler(
            signal_file,
            maxBytes=self.logging_config.get('max_log_size_mb', 10) * 1024 * 1024,
            backupCount=self.logging_config.get('backup_count', 5)
        )
        signal_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        signal_handler.setFormatter(signal_formatter)
        logger.addHandler(signal_handler)
        
        self.loggers['signals'] = logger
    
    def _setup_error_logger(self):
        """Setup error-specific logger"""
        logger = logging.getLogger('trading_errors')
        logger.setLevel(logging.ERROR)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Error file handler
        error_file = os.path.join('logs', 'errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=self.logging_config.get('max_log_size_mb', 10) * 1024 * 1024,
            backupCount=self.logging_config.get('backup_count', 5)
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
        
        self.loggers['errors'] = logger
    
    def _setup_performance_logger(self):
        """Setup performance monitoring logger"""
        logger = logging.getLogger('trading_performance')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Performance file handler
        perf_file = os.path.join('logs', 'performance.log')
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_file,
            maxBytes=self.logging_config.get('max_log_size_mb', 10) * 1024 * 1024,
            backupCount=self.logging_config.get('backup_count', 5)
        )
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        logger.addHandler(perf_handler)
        
        self.loggers['performance'] = logger
    
    def info(self, message: str, logger_name: str = 'main'):
        """Log info message"""
        self.loggers.get(logger_name, self.loggers['main']).info(message)
    
    def warning(self, message: str, logger_name: str = 'main'):
        """Log warning message"""
        self.loggers.get(logger_name, self.loggers['main']).warning(message)
    
    def error(self, message: str, logger_name: str = 'errors'):
        """Log error message"""
        self.loggers.get(logger_name, self.loggers['errors']).error(message)
    
    def debug(self, message: str, logger_name: str = 'main'):
        """Log debug message"""
        self.loggers.get(logger_name, self.loggers['main']).debug(message)
    
    def log_signal(self, signal: Dict):
        """Log trading signal"""
        signal_data = {
            'timestamp': signal.get('timestamp', datetime.now()).isoformat(),
            'symbol': signal.get('symbol'),
            'timeframe': signal.get('timeframe'),
            'signal_type': signal.get('signal_type'),
            'signal_name': signal.get('signal_name'),
            'price': signal.get('current_price'),
            'rsi': signal.get('rsi'),
            'ema1': signal.get('ema1'),
            'ema2': signal.get('ema2'),
            'ema4': signal.get('ema4'),
            'volume': signal.get('volume')
        }
        
        # Log as JSON for easy parsing
        self.loggers['signals'].info(json.dumps(signal_data))
        
        # Also log as readable format
        readable_msg = (
            f"SIGNAL: {signal_data['signal_name']} | "
            f"{signal_data['symbol']} {signal_data['timeframe']} | "
            f"Price: ${signal_data['price']:.4f} | "
            f"RSI: {signal_data['rsi']:.2f}"
        )
        self.loggers['signals'].info(readable_msg)
    
    def log_scan_start(self, symbols: list, timeframes: list):
        """Log scan start"""
        total_combinations = len(symbols) * len(timeframes)
        self.info(f"Starting scan: {len(symbols)} symbols × {len(timeframes)} timeframes = {total_combinations} combinations")
    
    def log_scan_complete(self, signals_found: int, total_combinations: int, duration: float):
        """Log scan completion"""
        self.info(f"Scan completed: {signals_found} signals found in {total_combinations} combinations ({duration:.2f}s)")
    
    def log_performance(self, operation: str, duration: float, details: Dict = None):
        """Log performance metrics"""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_seconds': duration,
            'details': details or {}
        }
        
        self.loggers['performance'].info(json.dumps(perf_data))
    
    def log_error_with_context(self, error: Exception, context: Dict = None):
        """Log error with additional context"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.loggers['errors'].error(json.dumps(error_data))
        self.loggers['errors'].error(f"Error: {error}", exc_info=True)
    
    def log_alert_sent(self, signal: Dict, channel: str, success: bool):
        """Log alert sending"""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'signal': {
                'symbol': signal.get('symbol'),
                'timeframe': signal.get('timeframe'),
                'signal_name': signal.get('signal_name')
            },
            'channel': channel,
            'success': success
        }
        
        self.loggers['signals'].info(json.dumps(alert_data))
    
    def log_data_fetch(self, symbol: str, timeframe: str, success: bool, duration: float, candles_count: int = None):
        """Log data fetching operation"""
        fetch_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'timeframe': timeframe,
            'success': success,
            'duration_seconds': duration,
            'candles_count': candles_count
        }
        
        self.loggers['performance'].info(json.dumps(fetch_data))
    
    def get_log_stats(self) -> Dict:
        """Get logging statistics"""
        stats = {
            'log_files': [],
            'total_size_mb': 0
        }
        
        log_dir = 'logs'
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    stats['log_files'].append({
                        'filename': filename,
                        'size_mb': round(size_mb, 2)
                    })
                    stats['total_size_mb'] += size_mb
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        cleaned_files = []
        
        log_dir = 'logs'
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.getmtime(filepath) < cutoff_time:
                        try:
                            os.remove(filepath)
                            cleaned_files.append(filename)
                        except Exception as e:
                            self.error(f"Failed to delete {filename}: {e}")
        
        if cleaned_files:
            self.info(f"Cleaned up {len(cleaned_files)} old log files: {cleaned_files}")
        
        return cleaned_files
    
    def test_logging(self):
        """Test all logging functions"""
        self.info("Testing main logger")
        self.warning("Testing warning logger")
        self.error("Testing error logger")
        self.debug("Testing debug logger")
        
        # Test signal logging
        test_signal = {
            'timestamp': datetime.now(),
            'symbol': 'BTCUSDT',
            'timeframe': '5m',
            'signal_type': 1,
            'signal_name': 'BUY_30',
            'current_price': 50000.0,
            'rsi': 45.5,
            'ema1': 49950.0,
            'ema2': 49900.0,
            'ema4': 49800.0,
            'volume': 1000000
        }
        self.log_signal(test_signal)
        
        # Test performance logging
        self.log_performance("test_operation", 1.5, {"test": True})
        
        self.info("Logging test completed")