"""
Configuration file for multi-symbol multi-timeframe trading signals
"""

# Trading symbols (up to 20 symbols)
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT",
    "SOLUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT",
    "MATICUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "FILUSDT",
    "TRXUSDT", "ETCUSDT", "XLMUSDT", "VETUSDT", "ICPUSDT"
]

# Timeframes to monitor
TIMEFRAMES = [
    "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"
]

# Signal types
SIGNAL_TYPES = {
    1: "BUY_30",      # Buy signal on 30-period EMA
    2: "SELL_30",     # Sell signal on 30-period EMA  
    3: "BUY_60",      # Buy signal on 60-period EMA
    4: "SELL_60",     # Sell signal on 60-period EMA
    5: "NO_SIGNAL"    # No signal
}

# Alert settings
ALERT_SETTINGS = {
    "enable_telegram": True,
    "enable_console": True,
    "enable_file_log": True,
    "log_file": "trading_signals.log"
}

# Exchange settings
EXCHANGE_SETTINGS = {
    "exchange": "binance",
    "sandbox": False,  # Set to True for testing
    "rate_limit": 1200  # requests per minute
}

# Vanguard function parameters
VANGUARD_PARAMS = {
    "ema_periods": [30, 60, 144, 240],
    "rsi_period": 14,
    "rsi_low": 38,
    "rsi_high": 61,
    "rsi_low2": 38,
    "rsi_high2": 61,
    "cci_period": 20,
    "cci_low": -100,
    "cci_high": 100,
    "iscci": False,
    "iswvap": False
}