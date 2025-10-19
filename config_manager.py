"""
Configuration management system
Handles loading and validation of configuration settings
"""

import os
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from config import SYMBOLS, TIMEFRAMES, ALERT_SETTINGS, EXCHANGE_SETTINGS, VANGUARD_PARAMS


class ConfigManager:
    """
    Manages configuration settings for the trading system
    """
    
    def __init__(self, config_file: str = None, env_file: str = None):
        self.config_file = config_file or "config.json"
        self.env_file = env_file or ".env"
        self.config = {}
        
        # Load environment variables
        self._load_env()
        
        # Load configuration
        self._load_config()
    
    def _load_env(self):
        """Load environment variables from .env file"""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            print(f"✓ Loaded environment variables from {self.env_file}")
        else:
            print(f"⚠ No {self.env_file} file found, using default values")
    
    def _load_config(self):
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"✓ Loaded configuration from {self.config_file}")
            except Exception as e:
                print(f"✗ Error loading config file: {e}")
                self.config = self._get_default_config()
        else:
            print(f"⚠ No {self.config_file} file found, using default configuration")
            self.config = self._get_default_config()
            self.save_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "symbols": SYMBOLS,
            "timeframes": TIMEFRAMES,
            "alert_settings": ALERT_SETTINGS,
            "exchange_settings": EXCHANGE_SETTINGS,
            "vanguard_params": VANGUARD_PARAMS,
            "scanning": {
                "scan_interval_minutes": 5,
                "max_workers": 5,
                "rate_limit_per_minute": 1200,
                "enable_priority_scanning": True,
                "cooldown_minutes": 30
            },
            "data": {
                "candle_limit": 500,
                "min_candles_for_analysis": 200,
                "enable_data_caching": True,
                "cache_duration_minutes": 5
            },
            "logging": {
                "level": "INFO",
                "log_file": "trading_signals.log",
                "max_log_size_mb": 10,
                "backup_count": 5
            }
        }
    
    def get_symbols(self) -> List[str]:
        """Get list of symbols to monitor"""
        # Check environment variable first
        env_symbols = os.getenv('SYMBOLS')
        if env_symbols:
            return [s.strip() for s in env_symbols.split(',') if s.strip()]
        
        # Fall back to config file
        return self.config.get('symbols', SYMBOLS)
    
    def get_timeframes(self) -> List[str]:
        """Get list of timeframes to monitor"""
        # Check environment variable first
        env_timeframes = os.getenv('TIMEFRAMES')
        if env_timeframes:
            return [t.strip() for t in env_timeframes.split(',') if t.strip()]
        
        # Fall back to config file
        return self.config.get('timeframes', TIMEFRAMES)
    
    def get_alert_settings(self) -> Dict:
        """Get alert settings"""
        settings = self.config.get('alert_settings', ALERT_SETTINGS.copy())
        
        # Override with environment variables
        if os.getenv('ENABLE_TELEGRAM_ALERTS'):
            settings['enable_telegram'] = os.getenv('ENABLE_TELEGRAM_ALERTS').lower() == 'true'
        if os.getenv('ENABLE_CONSOLE_ALERTS'):
            settings['enable_console'] = os.getenv('ENABLE_CONSOLE_ALERTS').lower() == 'true'
        if os.getenv('ENABLE_FILE_LOGGING'):
            settings['enable_file_log'] = os.getenv('ENABLE_FILE_LOGGING').lower() == 'true'
        
        return settings
    
    def get_exchange_settings(self) -> Dict:
        """Get exchange settings"""
        settings = self.config.get('exchange_settings', EXCHANGE_SETTINGS.copy())
        
        # Override with environment variables
        if os.getenv('EXCHANGE_API_KEY'):
            settings['api_key'] = os.getenv('EXCHANGE_API_KEY')
        if os.getenv('EXCHANGE_SECRET'):
            settings['secret'] = os.getenv('EXCHANGE_SECRET')
        if os.getenv('EXCHANGE_PASSPHRASE'):
            settings['passphrase'] = os.getenv('EXCHANGE_PASSPHRASE')
        
        return settings
    
    def get_telegram_credentials(self) -> tuple:
        """Get Telegram bot credentials"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        return token, chat_id
    
    def get_scanning_settings(self) -> Dict:
        """Get scanning settings"""
        settings = self.config.get('scanning', {})
        
        # Override with environment variables
        if os.getenv('SCAN_INTERVAL_MINUTES'):
            settings['scan_interval_minutes'] = int(os.getenv('SCAN_INTERVAL_MINUTES'))
        if os.getenv('MAX_WORKERS'):
            settings['max_workers'] = int(os.getenv('MAX_WORKERS'))
        if os.getenv('RATE_LIMIT_PER_MINUTE'):
            settings['rate_limit_per_minute'] = int(os.getenv('RATE_LIMIT_PER_MINUTE'))
        
        return settings
    
    def get_data_settings(self) -> Dict:
        """Get data fetching settings"""
        return self.config.get('data', {})
    
    def get_logging_settings(self) -> Dict:
        """Get logging settings"""
        return self.config.get('logging', {})
    
    def get_vanguard_params(self) -> Dict:
        """Get Vanguard strategy parameters"""
        return self.config.get('vanguard_params', VANGUARD_PARAMS)
    
    def update_config(self, section: str, key: str, value: Any):
        """Update a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✓ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate symbols
        symbols = self.get_symbols()
        if not symbols:
            issues.append("No symbols configured")
        elif len(symbols) > 20:
            issues.append(f"Too many symbols configured ({len(symbols)}), maximum is 20")
        
        # Validate timeframes
        timeframes = self.get_timeframes()
        if not timeframes:
            issues.append("No timeframes configured")
        
        valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d']
        invalid_timeframes = [tf for tf in timeframes if tf not in valid_timeframes]
        if invalid_timeframes:
            issues.append(f"Invalid timeframes: {invalid_timeframes}")
        
        # Validate alert settings
        alert_settings = self.get_alert_settings()
        if alert_settings.get('enable_telegram', False):
            token, chat_id = self.get_telegram_credentials()
            if not token:
                issues.append("Telegram alerts enabled but no bot token provided")
            if not chat_id:
                issues.append("Telegram alerts enabled but no chat ID provided")
        
        # Validate scanning settings
        scanning_settings = self.get_scanning_settings()
        if scanning_settings.get('max_workers', 1) < 1:
            issues.append("Max workers must be at least 1")
        if scanning_settings.get('scan_interval_minutes', 1) < 1:
            issues.append("Scan interval must be at least 1 minute")
        
        return issues
    
    def get_config_summary(self) -> Dict:
        """Get a summary of current configuration"""
        return {
            'symbols_count': len(self.get_symbols()),
            'timeframes_count': len(self.get_timeframes()),
            'alert_channels': sum([
                self.get_alert_settings().get('enable_console', False),
                self.get_alert_settings().get('enable_file_log', False),
                self.get_alert_settings().get('enable_telegram', False)
            ]),
            'scan_interval': self.get_scanning_settings().get('scan_interval_minutes', 5),
            'max_workers': self.get_scanning_settings().get('max_workers', 5),
            'total_combinations': len(self.get_symbols()) * len(self.get_timeframes())
        }
    
    def create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = self._get_default_config()
        
        # Add some sample customizations
        sample_config['symbols'] = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT']
        sample_config['timeframes'] = ['1m', '5m', '15m', '1h', '4h']
        sample_config['scanning']['scan_interval_minutes'] = 2
        sample_config['scanning']['max_workers'] = 3
        
        with open('config_sample.json', 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print("✓ Sample configuration created: config_sample.json")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._get_default_config()
        self.save_config()
        print("✓ Configuration reset to defaults")