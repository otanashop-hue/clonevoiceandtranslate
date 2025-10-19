#!/usr/bin/env python3
"""
Example script showing how to use the trading signal system
"""

from main import TradingSignalBot
from config_manager import ConfigManager
import time


def example_single_scan():
    """Example: Run a single scan"""
    print("=" * 60)
    print("EXAMPLE: Single Scan")
    print("=" * 60)
    
    # Create bot instance
    bot = TradingSignalBot()
    
    # Run single scan
    success = bot.run_once()
    
    if success:
        print("✓ Single scan completed successfully")
    else:
        print("✗ Single scan failed")


def example_custom_configuration():
    """Example: Use custom configuration"""
    print("=" * 60)
    print("EXAMPLE: Custom Configuration")
    print("=" * 60)
    
    # Create custom configuration
    config_manager = ConfigManager()
    
    # Update symbols (limit to 5 for example)
    config_manager.update_config('symbols', 'symbols', [
        'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT'
    ])
    
    # Update timeframes (limit to 3 for example)
    config_manager.update_config('timeframes', 'timeframes', [
        '1m', '5m', '1h'
    ])
    
    # Update scan interval
    config_manager.update_config('scanning', 'scan_interval_minutes', 2)
    
    # Create bot with custom config
    bot = TradingSignalBot('config.json')
    
    print("Custom configuration:")
    print(f"  Symbols: {config_manager.get_symbols()}")
    print(f"  Timeframes: {config_manager.get_timeframes()}")
    print(f"  Scan interval: {config_manager.get_scanning_settings()['scan_interval_minutes']} minutes")
    
    # Run single scan with custom config
    success = bot.run_once()
    
    if success:
        print("✓ Custom configuration scan completed")
    else:
        print("✗ Custom configuration scan failed")


def example_continuous_monitoring():
    """Example: Continuous monitoring (runs for 2 minutes)"""
    print("=" * 60)
    print("EXAMPLE: Continuous Monitoring (2 minutes)")
    print("=" * 60)
    
    # Create bot instance
    bot = TradingSignalBot()
    
    # Start bot
    if bot.start():
        print("✓ Bot started, monitoring for 2 minutes...")
        
        # Monitor for 2 minutes
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minutes
            time.sleep(10)  # Check every 10 seconds
            status = bot.get_status()
            print(f"Status: {status['total_scans']} scans, {status['total_signals']} signals")
        
        # Stop bot
        bot.stop()
        print("✓ Monitoring completed")
    else:
        print("✗ Failed to start bot")


def example_alert_testing():
    """Example: Test alert system"""
    print("=" * 60)
    print("EXAMPLE: Alert System Testing")
    print("=" * 60)
    
    from alert_system import AlertSystem
    
    # Create alert system
    alert_system = AlertSystem()
    
    # Test alerts
    success = alert_system.test_alerts()
    
    if success:
        print("✓ Alert system test passed")
    else:
        print("✗ Alert system test failed")


def example_data_analysis():
    """Example: Analyze data for a specific symbol"""
    print("=" * 60)
    print("EXAMPLE: Data Analysis")
    print("=" * 60)
    
    from data_fetcher import DataFetcher
    from vanguard_strategy import VanguardStrategy
    
    # Create components
    data_fetcher = DataFetcher()
    strategy = VanguardStrategy()
    
    # Fetch data for BTCUSDT
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    print(f"Fetching data for {symbol} {timeframe}...")
    df = data_fetcher.fetch_ohlcv(symbol, timeframe, limit=500)
    
    if df is not None:
        print(f"✓ Fetched {len(df)} candles")
        
        # Calculate indicators
        df_with_indicators = strategy.calculate_indicators(df)
        
        # Show latest values
        latest = df_with_indicators.iloc[-1]
        print(f"\nLatest values for {symbol} {timeframe}:")
        print(f"  Price: ${latest['close']:.4f}")
        print(f"  RSI: {latest['rsi']:.2f}")
        print(f"  EMA1: {latest['ema1']:.4f}")
        print(f"  EMA2: {latest['ema2']:.4f}")
        print(f"  EMA4: {latest['ema4']:.4f}")
        print(f"  Volume: {latest['volume']:,.0f}")
        
        # Get signal
        signal_type = strategy.f_vanguard(df_with_indicators)
        signal_names = {1: 'BUY_30', 2: 'SELL_30', 3: 'BUY_60', 4: 'SELL_60', 5: 'NO_SIGNAL'}
        print(f"  Signal: {signal_names.get(signal_type, 'UNKNOWN')}")
        
    else:
        print(f"✗ Failed to fetch data for {symbol}")


def main():
    """Run all examples"""
    print("Multi-Symbol Multi-Timeframe Trading Signal System")
    print("Example Usage Scripts")
    print("=" * 60)
    
    try:
        # Example 1: Single scan
        example_single_scan()
        print()
        
        # Example 2: Custom configuration
        example_custom_configuration()
        print()
        
        # Example 3: Alert testing
        example_alert_testing()
        print()
        
        # Example 4: Data analysis
        example_data_analysis()
        print()
        
        # Example 5: Continuous monitoring (optional - uncomment to run)
        # example_continuous_monitoring()
        
        print("=" * 60)
        print("All examples completed!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")


if __name__ == "__main__":
    main()