#!/usr/bin/env python3
"""
Multi-Symbol Multi-Timeframe Trading Signal Scanner
Main execution script for the Vanguard trading strategy
"""

import sys
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse

from config_manager import ConfigManager
from signal_scanner import SignalScanner
from alert_system import AlertSystem
from logger import TradingLogger
from data_fetcher import DataFetcher


class TradingSignalBot:
    """
    Main trading signal bot that orchestrates all components
    """
    
    def __init__(self, config_file: str = None):
        self.running = False
        self.scan_thread = None
        self.last_scan_time = None
        
        # Initialize components
        self.config_manager = ConfigManager(config_file)
        self.logger = TradingLogger(self.config_manager)
        self.scanner = SignalScanner(
            max_workers=self.config_manager.get_scanning_settings().get('max_workers', 5)
        )
        
        # Setup alert system
        telegram_token, telegram_chat_id = self.config_manager.get_telegram_credentials()
        self.alert_system = AlertSystem(telegram_token, telegram_chat_id)
        
        # Setup data fetcher
        self.data_fetcher = DataFetcher()
        
        # Statistics
        self.stats = {
            'total_scans': 0,
            'total_signals': 0,
            'signals_by_type': {},
            'signals_by_symbol': {},
            'start_time': None,
            'last_scan_duration': 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def validate_configuration(self) -> bool:
        """Validate configuration and return True if valid"""
        issues = self.config_manager.validate_config()
        
        if issues:
            self.logger.error("Configuration validation failed:")
            for issue in issues:
                self.logger.error(f"  - {issue}")
            return False
        
        self.logger.info("✓ Configuration validation passed")
        return True
    
    def test_components(self) -> bool:
        """Test all components and return True if all tests pass"""
        self.logger.info("Testing components...")
        
        # Test data fetcher
        try:
            test_symbol = self.config_manager.get_symbols()[0]
            test_timeframe = self.config_manager.get_timeframes()[0]
            self.logger.info(f"Testing data fetch for {test_symbol} {test_timeframe}...")
            
            df = self.data_fetcher.fetch_ohlcv(test_symbol, test_timeframe, limit=100)
            if df is None or len(df) < 50:
                self.logger.error("Data fetcher test failed")
                return False
            
            self.logger.info("✓ Data fetcher test passed")
        except Exception as e:
            self.logger.error(f"Data fetcher test failed: {e}")
            return False
        
        # Test strategy
        try:
            self.logger.info("Testing Vanguard strategy...")
            signal_type = self.scanner.strategy.f_vanguard(df)
            self.logger.info(f"✓ Strategy test passed (signal: {signal_type})")
        except Exception as e:
            self.logger.error(f"Strategy test failed: {e}")
            return False
        
        # Test alert system
        try:
            self.logger.info("Testing alert system...")
            success = self.alert_system.test_alerts()
            if not success:
                self.logger.warning("Alert system test failed, but continuing...")
            else:
                self.logger.info("✓ Alert system test passed")
        except Exception as e:
            self.logger.error(f"Alert system test failed: {e}")
            return False
        
        self.logger.info("✓ All component tests passed")
        return True
    
    def run_single_scan(self) -> List[Dict]:
        """Run a single scan and return signals found"""
        start_time = time.time()
        
        symbols = self.config_manager.get_symbols()
        timeframes = self.config_manager.get_timeframes()
        
        self.logger.log_scan_start(symbols, timeframes)
        
        # Run scan based on configuration
        scanning_settings = self.config_manager.get_scanning_settings()
        if scanning_settings.get('enable_priority_scanning', True):
            signals = self.scanner.scan_priority_combinations(symbols, timeframes)
        else:
            signals = self.scanner.scan_all_combinations(symbols, timeframes)
        
        duration = time.time() - start_time
        self.logger.log_scan_complete(len(signals), len(symbols) * len(timeframes), duration)
        
        # Update statistics
        self.stats['total_scans'] += 1
        self.stats['total_signals'] += len(signals)
        self.stats['last_scan_duration'] = duration
        self.last_scan_time = datetime.now()
        
        # Update signal statistics
        for signal in signals:
            signal_type = signal['signal_name']
            symbol = signal['symbol']
            
            self.stats['signals_by_type'][signal_type] = self.stats['signals_by_type'].get(signal_type, 0) + 1
            self.stats['signals_by_symbol'][symbol] = self.stats['signals_by_symbol'].get(symbol, 0) + 1
        
        return signals
    
    def process_signals(self, signals: List[Dict]) -> Dict:
        """Process and send alerts for signals"""
        if not signals:
            return {'processed': 0, 'sent': 0, 'skipped': 0}
        
        processed = 0
        sent = 0
        skipped = 0
        
        for signal in signals:
            processed += 1
            
            # Check if we should alert (cooldown)
            cooldown_minutes = self.config_manager.get_scanning_settings().get('cooldown_minutes', 30)
            if not self.alert_system.should_alert(signal, cooldown_minutes):
                skipped += 1
                self.logger.debug(f"Skipping alert for {signal['symbol']} {signal['timeframe']} (cooldown)")
                continue
            
            # Log signal
            self.logger.log_signal(signal)
            
            # Send alert
            success = self.alert_system.send_alert(signal)
            if success:
                sent += 1
            else:
                self.logger.error(f"Failed to send alert for {signal['symbol']} {signal['timeframe']}")
        
        return {
            'processed': processed,
            'sent': sent,
            'skipped': skipped
        }
    
    def scan_loop(self):
        """Main scanning loop"""
        self.logger.info("Starting scan loop...")
        
        scan_interval = self.config_manager.get_scanning_settings().get('scan_interval_minutes', 5)
        
        while self.running:
            try:
                # Run scan
                signals = self.run_single_scan()
                
                # Process signals
                if signals:
                    result = self.process_signals(signals)
                    self.logger.info(
                        f"Processed {result['processed']} signals: "
                        f"{result['sent']} sent, {result['skipped']} skipped"
                    )
                else:
                    self.logger.info("No signals found in this scan")
                
                # Wait for next scan
                self.logger.info(f"Waiting {scan_interval} minutes until next scan...")
                time.sleep(scan_interval * 60)
                
            except Exception as e:
                self.logger.error_with_context(e, {'operation': 'scan_loop'})
                time.sleep(60)  # Wait 1 minute before retrying
    
    def start(self):
        """Start the trading bot"""
        if self.running:
            self.logger.warning("Bot is already running")
            return
        
        self.logger.info("Starting Multi-Symbol Multi-Timeframe Trading Signal Bot")
        self.logger.info("=" * 60)
        
        # Validate configuration
        if not self.validate_configuration():
            self.logger.error("Configuration validation failed. Exiting.")
            return False
        
        # Test components
        if not self.test_components():
            self.logger.error("Component tests failed. Exiting.")
            return False
        
        # Show configuration summary
        config_summary = self.config_manager.get_config_summary()
        self.logger.info("Configuration Summary:")
        self.logger.info(f"  Symbols: {config_summary['symbols_count']}")
        self.logger.info(f"  Timeframes: {config_summary['timeframes_count']}")
        self.logger.info(f"  Total combinations: {config_summary['total_combinations']}")
        self.logger.info(f"  Scan interval: {config_summary['scan_interval']} minutes")
        self.logger.info(f"  Max workers: {config_summary['max_workers']}")
        self.logger.info(f"  Alert channels: {config_summary['alert_channels']}")
        
        # Start bot
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Start scan loop in separate thread
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()
        
        self.logger.info("✓ Bot started successfully")
        return True
    
    def stop(self):
        """Stop the trading bot"""
        if not self.running:
            return
        
        self.logger.info("Stopping trading bot...")
        self.running = False
        
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=10)
        
        self.logger.info("✓ Bot stopped")
    
    def run_once(self) -> bool:
        """Run a single scan and exit"""
        self.logger.info("Running single scan...")
        
        if not self.validate_configuration():
            return False
        
        if not self.test_components():
            return False
        
        # Run single scan
        signals = self.run_single_scan()
        
        if signals:
            result = self.process_signals(signals)
            self.logger.info(f"Scan complete: {result['sent']} alerts sent")
        else:
            self.logger.info("Scan complete: No signals found")
        
        return True
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        uptime = None
        if self.stats['start_time']:
            uptime = datetime.now() - self.stats['start_time']
        
        return {
            'running': self.running,
            'uptime_seconds': uptime.total_seconds() if uptime else None,
            'total_scans': self.stats['total_scans'],
            'total_signals': self.stats['total_signals'],
            'last_scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'last_scan_duration': self.stats['last_scan_duration'],
            'signals_by_type': self.stats['signals_by_type'],
            'signals_by_symbol': self.stats['signals_by_symbol']
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("TRADING BOT STATUS")
        print("=" * 50)
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        
        if status['uptime_seconds']:
            hours = int(status['uptime_seconds'] // 3600)
            minutes = int((status['uptime_seconds'] % 3600) // 60)
            print(f"Uptime: {hours}h {minutes}m")
        
        print(f"Total scans: {status['total_scans']}")
        print(f"Total signals: {status['total_signals']}")
        
        if status['last_scan_time']:
            print(f"Last scan: {status['last_scan_time']}")
            print(f"Last scan duration: {status['last_scan_duration']:.2f}s")
        
        if status['signals_by_type']:
            print("\nSignals by type:")
            for signal_type, count in status['signals_by_type'].items():
                print(f"  {signal_type}: {count}")
        
        if status['signals_by_symbol']:
            print("\nTop symbols with signals:")
            sorted_symbols = sorted(status['signals_by_symbol'].items(), key=lambda x: x[1], reverse=True)
            for symbol, count in sorted_symbols[:10]:  # Top 10
                print(f"  {symbol}: {count}")
        
        print("=" * 50)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Multi-Symbol Multi-Timeframe Trading Signal Scanner')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--once', action='store_true', help='Run single scan and exit')
    parser.add_argument('--test', action='store_true', help='Test configuration and components')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = TradingSignalBot(args.config)
    
    if args.test:
        # Test mode
        print("Testing configuration and components...")
        if bot.validate_configuration() and bot.test_components():
            print("✓ All tests passed")
            sys.exit(0)
        else:
            print("✗ Tests failed")
            sys.exit(1)
    
    elif args.once:
        # Single scan mode
        success = bot.run_once()
        sys.exit(0 if success else 1)
    
    elif args.status:
        # Status mode
        bot.print_status()
        sys.exit(0)
    
    else:
        # Continuous mode
        try:
            if bot.start():
                # Keep main thread alive
                while bot.running:
                    time.sleep(1)
            else:
                sys.exit(1)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
        finally:
            bot.stop()


if __name__ == "__main__":
    main()