"""
Alert system for trading signals
Supports multiple alert channels: Console, File, Telegram
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
from config import ALERT_SETTINGS


class AlertSystem:
    """
    Handles alert notifications for trading signals
    """
    
    def __init__(self, telegram_token: str = None, telegram_chat_id: str = None):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.log_file = ALERT_SETTINGS.get("log_file", "trading_signals.log")
        
        # Setup logging
        self._setup_logging()
        
        # Alert counters
        self.alert_count = 0
        self.last_alert_time = {}
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def send_console_alert(self, signal: Dict) -> bool:
        """Send alert to console"""
        try:
            if not ALERT_SETTINGS.get("enable_console", True):
                return True
            
            # Format alert message
            message = self._format_alert_message(signal)
            
            # Print with colors (if supported)
            signal_type = signal.get('signal_name', 'UNKNOWN')
            if 'BUY' in signal_type:
                print(f"\n🟢 {message}")
            elif 'SELL' in signal_type:
                print(f"\n🔴 {message}")
            else:
                print(f"\n⚪ {message}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending console alert: {e}")
            return False
    
    def send_file_alert(self, signal: Dict) -> bool:
        """Send alert to file"""
        try:
            if not ALERT_SETTINGS.get("enable_file_log", True):
                return True
            
            # Format alert message
            message = self._format_alert_message(signal)
            
            # Log to file
            self.logger.info(f"ALERT: {message}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending file alert: {e}")
            return False
    
    def send_telegram_alert(self, signal: Dict) -> bool:
        """Send alert via Telegram"""
        try:
            if not ALERT_SETTINGS.get("enable_telegram", False):
                return True
            
            if not self.telegram_token or not self.telegram_chat_id:
                self.logger.warning("Telegram credentials not configured")
                return False
            
            # Format alert message
            message = self._format_telegram_message(signal)
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"Telegram alert sent successfully for {signal['symbol']}")
                return True
            else:
                self.logger.error(f"Telegram alert failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending Telegram alert: {e}")
            return False
    
    def send_alert(self, signal: Dict) -> bool:
        """
        Send alert through all configured channels
        
        Args:
            signal: Signal information dictionary
            
        Returns:
            True if at least one channel succeeded
        """
        success_count = 0
        total_channels = 0
        
        # Console alert
        if ALERT_SETTINGS.get("enable_console", True):
            total_channels += 1
            if self.send_console_alert(signal):
                success_count += 1
        
        # File alert
        if ALERT_SETTINGS.get("enable_file_log", True):
            total_channels += 1
            if self.send_file_alert(signal):
                success_count += 1
        
        # Telegram alert
        if ALERT_SETTINGS.get("enable_telegram", False):
            total_channels += 1
            if self.send_telegram_alert(signal):
                success_count += 1
        
        # Update counters
        self.alert_count += 1
        signal_key = f"{signal['symbol']}_{signal['timeframe']}_{signal['signal_name']}"
        self.last_alert_time[signal_key] = datetime.now()
        
        success = success_count > 0
        if success:
            self.logger.info(f"Alert sent successfully ({success_count}/{total_channels} channels)")
        else:
            self.logger.error(f"All alert channels failed for {signal['symbol']}")
        
        return success
    
    def send_batch_alerts(self, signals: List[Dict]) -> Dict:
        """
        Send alerts for multiple signals
        
        Args:
            signals: List of signal dictionaries
            
        Returns:
            Summary of alert results
        """
        results = {
            'total_signals': len(signals),
            'successful_alerts': 0,
            'failed_alerts': 0,
            'by_signal_type': {},
            'by_symbol': {}
        }
        
        for signal in signals:
            success = self.send_alert(signal)
            
            if success:
                results['successful_alerts'] += 1
            else:
                results['failed_alerts'] += 1
            
            # Count by signal type
            signal_type = signal.get('signal_name', 'UNKNOWN')
            results['by_signal_type'][signal_type] = results['by_signal_type'].get(signal_type, 0) + 1
            
            # Count by symbol
            symbol = signal.get('symbol', 'UNKNOWN')
            results['by_symbol'][symbol] = results['by_symbol'].get(symbol, 0) + 1
        
        return results
    
    def _format_alert_message(self, signal: Dict) -> str:
        """Format alert message for console/file output"""
        timestamp = signal.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        symbol = signal.get('symbol', 'UNKNOWN')
        timeframe = signal.get('timeframe', 'UNKNOWN')
        signal_name = signal.get('signal_name', 'UNKNOWN')
        price = signal.get('current_price', 0)
        rsi = signal.get('rsi', 0)
        
        message = (
            f"[{timestamp}] {signal_name} | "
            f"{symbol} {timeframe} | "
            f"Price: ${price:.4f} | "
            f"RSI: {rsi:.2f}"
        )
        
        return message
    
    def _format_telegram_message(self, signal: Dict) -> str:
        """Format alert message for Telegram"""
        timestamp = signal.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        symbol = signal.get('symbol', 'UNKNOWN')
        timeframe = signal.get('timeframe', 'UNKNOWN')
        signal_name = signal.get('signal_name', 'UNKNOWN')
        price = signal.get('current_price', 0)
        rsi = signal.get('rsi', 0)
        ema1 = signal.get('ema1', 0)
        ema2 = signal.get('ema2', 0)
        ema4 = signal.get('ema4', 0)
        volume = signal.get('volume', 0)
        
        # Choose emoji based on signal type
        emoji = "🟢" if "BUY" in signal_name else "🔴" if "SELL" in signal_name else "⚪"
        
        message = f"""
{emoji} <b>{signal_name}</b>
📊 <b>{symbol}</b> - {timeframe}
💰 Price: <b>${price:.4f}</b>
📈 RSI: {rsi:.2f}
📊 EMAs: {ema1:.4f} | {ema2:.4f} | {ema4:.4f}
📦 Volume: {volume:,.0f}
⏰ {timestamp}
        """.strip()
        
        return message
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        return {
            'total_alerts_sent': self.alert_count,
            'unique_signals_alerted': len(self.last_alert_time),
            'last_alert_times': self.last_alert_time
        }
    
    def should_alert(self, signal: Dict, cooldown_minutes: int = 30) -> bool:
        """
        Check if we should send an alert (avoid spam)
        
        Args:
            signal: Signal information
            cooldown_minutes: Minimum minutes between alerts for same signal
            
        Returns:
            True if should alert, False otherwise
        """
        signal_key = f"{signal['symbol']}_{signal['timeframe']}_{signal['signal_name']}"
        
        if signal_key not in self.last_alert_time:
            return True
        
        last_alert = self.last_alert_time[signal_key]
        time_diff = datetime.now() - last_alert
        
        return time_diff.total_seconds() > (cooldown_minutes * 60)
    
    def test_alerts(self):
        """Test all alert channels with a sample signal"""
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
        
        print("Testing alert system...")
        success = self.send_alert(test_signal)
        
        if success:
            print("✓ Alert system test successful")
        else:
            print("✗ Alert system test failed")
        
        return success