# Multi-Symbol Multi-Timeframe Trading Signal Scanner

A comprehensive trading signal system that monitors up to 20 cryptocurrency symbols across multiple timeframes using the Vanguard trading strategy.

## Features

- **Multi-Symbol Support**: Monitor up to 20 trading symbols simultaneously
- **Multi-Timeframe Analysis**: Support for 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d timeframes
- **Vanguard Strategy**: Advanced trading strategy based on EMA crossovers, RSI, and CCI indicators
- **Real-time Alerts**: Multiple alert channels (Console, File, Telegram)
- **Parallel Processing**: Efficient scanning using multi-threading
- **Comprehensive Logging**: Detailed logs for signals, errors, and performance
- **Configurable**: Easy configuration through JSON files and environment variables

## Strategy Overview

The Vanguard strategy implements a sophisticated trading algorithm that generates four types of signals:

1. **BUY_30**: Buy signal based on 30-period EMA
2. **SELL_30**: Sell signal based on 30-period EMA  
3. **BUY_60**: Buy signal based on 60-period EMA
4. **SELL_60**: Sell signal based on 60-period EMA

### Key Indicators Used:
- **EMAs**: 30, 60, 144, 240 period exponential moving averages
- **RSI**: 14-period relative strength index
- **CCI**: 20-period commodity channel index
- **VWAP**: Volume weighted average price
- **Pivot Points**: For identifying overbought/oversold conditions

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd multi-symbol-trading-signals
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment** (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

## Quick Start

### 1. Basic Usage

Run a single scan to test the system:
```bash
python main.py --once
```

### 2. Continuous Monitoring

Start continuous monitoring:
```bash
python main.py
```

### 3. Test Configuration

Test your configuration and components:
```bash
python main.py --test
```

### 4. Check Status

View current bot status:
```bash
python main.py --status
```

## Configuration

### Environment Variables (.env file)

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Exchange Configuration
EXCHANGE_API_KEY=your_exchange_api_key_here
EXCHANGE_SECRET=your_exchange_secret_here

# Alert Settings
ENABLE_TELEGRAM_ALERTS=true
ENABLE_CONSOLE_ALERTS=true
ENABLE_FILE_LOGGING=true

# Scanning Settings
SCAN_INTERVAL_MINUTES=5
MAX_WORKERS=5
RATE_LIMIT_PER_MINUTE=1200

# Symbols to monitor (comma-separated)
SYMBOLS=BTCUSDT,ETHUSDT,ADAUSDT,BNBUSDT,XRPUSDT

# Timeframes to monitor (comma-separated)
TIMEFRAMES=1m,3m,5m,15m,30m,1h,2h,4h,6h,12h,1d
```

### Configuration File (config.json)

The system automatically creates a `config.json` file with default settings. You can modify this file to customize:

- Symbols to monitor
- Timeframes to scan
- Alert settings
- Scanning parameters
- Strategy parameters

## Usage Examples

### Example 1: Run Examples

```bash
python run_example.py
```

### Example 2: Custom Configuration

```python
from main import TradingSignalBot
from config_manager import ConfigManager

# Create custom configuration
config_manager = ConfigManager()
config_manager.update_config('symbols', 'symbols', ['BTCUSDT', 'ETHUSDT'])
config_manager.update_config('timeframes', 'timeframes', ['1m', '5m', '1h'])

# Run with custom config
bot = TradingSignalBot('config.json')
bot.run_once()
```

### Example 3: Direct Strategy Usage

```python
from vanguard_strategy import VanguardStrategy
from data_fetcher import DataFetcher

# Fetch data
data_fetcher = DataFetcher()
df = data_fetcher.fetch_ohlcv('BTCUSDT', '1h', limit=500)

# Apply strategy
strategy = VanguardStrategy()
signal = strategy.f_vanguard(df)
print(f"Signal: {signal}")  # 1=BUY_30, 2=SELL_30, 3=BUY_60, 4=SELL_60, 5=NO_SIGNAL
```

## Alert System

The system supports multiple alert channels:

### Console Alerts
- Real-time display of signals in the terminal
- Color-coded messages (🟢 for buy, 🔴 for sell)

### File Logging
- Detailed logs saved to `logs/` directory
- Separate files for signals, errors, and performance
- Automatic log rotation

### Telegram Alerts
- Send alerts directly to Telegram
- Rich formatting with emojis and technical details
- Configure bot token and chat ID in `.env` file

## File Structure

```
├── main.py                 # Main execution script
├── config.py              # Default configuration
├── config_manager.py      # Configuration management
├── vanguard_strategy.py   # Trading strategy implementation
├── signal_scanner.py      # Multi-symbol scanner
├── data_fetcher.py        # Data fetching from exchanges
├── alert_system.py        # Alert notification system
├── logger.py              # Advanced logging system
├── run_example.py         # Example usage scripts
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── config.json           # Configuration file (auto-generated)
└── logs/                 # Log files directory
    ├── main.log
    ├── signals.log
    ├── errors.log
    └── performance.log
```

## API Reference

### TradingSignalBot Class

Main bot class that orchestrates all components.

```python
bot = TradingSignalBot(config_file='config.json')

# Start continuous monitoring
bot.start()

# Run single scan
bot.run_once()

# Stop monitoring
bot.stop()

# Get status
status = bot.get_status()
```

### VanguardStrategy Class

Implements the Vanguard trading strategy.

```python
strategy = VanguardStrategy()

# Calculate indicators
df_with_indicators = strategy.calculate_indicators(df)

# Get signal
signal_type = strategy.f_vanguard(df)
```

### SignalScanner Class

Scans multiple symbols and timeframes for signals.

```python
scanner = SignalScanner(max_workers=5)

# Scan all combinations
signals = scanner.scan_all_combinations(symbols, timeframes)

# Scan single symbol
signals = scanner.scan_symbol_all_timeframes('BTCUSDT', timeframes)
```

## Performance Considerations

- **Rate Limiting**: Built-in rate limiting to respect exchange API limits
- **Parallel Processing**: Multi-threaded scanning for faster execution
- **Data Caching**: Optional data caching to reduce API calls
- **Memory Management**: Efficient memory usage for large datasets

## Troubleshooting

### Common Issues

1. **No data received**: Check internet connection and exchange API status
2. **Rate limit exceeded**: Increase scan interval or reduce max workers
3. **Telegram alerts not working**: Verify bot token and chat ID
4. **Configuration errors**: Run `python main.py --test` to validate

### Debug Mode

Enable debug logging by modifying the logging level in `config.json`:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## Support

For support and questions:
- Create an issue in the repository
- Check the logs in the `logs/` directory
- Run `python main.py --test` to diagnose issues