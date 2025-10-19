"""
Data fetcher for multi-symbol multi-timeframe trading data
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime, timedelta
from config import EXCHANGE_SETTINGS, SYMBOLS, TIMEFRAMES


class DataFetcher:
    """
    Handles data fetching from cryptocurrency exchanges
    """
    
    def __init__(self, exchange_name: str = None, sandbox: bool = None):
        self.exchange_name = exchange_name or EXCHANGE_SETTINGS["exchange"]
        self.sandbox = sandbox if sandbox is not None else EXCHANGE_SETTINGS["sandbox"]
        self.rate_limit = EXCHANGE_SETTINGS["rate_limit"]
        self.last_request_time = 0
        self.request_count = 0
        self.minute_start = time.time()
        
        # Initialize exchange
        self.exchange = self._initialize_exchange()
    
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize the exchange connection"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'sandbox': self.sandbox,
                'rateLimit': 1000,  # 1 second between requests
                'enableRateLimit': True,
            })
            
            # Test connection
            exchange.load_markets()
            print(f"✓ Connected to {self.exchange_name} exchange")
            return exchange
            
        except Exception as e:
            print(f"✗ Failed to connect to {self.exchange_name}: {e}")
            raise
    
    def _rate_limit_check(self):
        """Implement rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.minute_start >= 60:
            self.request_count = 0
            self.minute_start = current_time
        
        # Check if we're within rate limits
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - (current_time - self.minute_start)
            if sleep_time > 0:
                print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.request_count = 0
                self.minute_start = time.time()
        
        # Ensure minimum time between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0:  # 1 second minimum between requests
            time.sleep(1.0 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data for a symbol and timeframe
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '1m', '5m', '1h')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            self._rate_limit_check()
            
            # Fetch data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                print(f"✗ No data received for {symbol} {timeframe}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Add required columns for strategy
            df['hl2'] = (df['high'] + df['low']) / 2
            df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
            
            print(f"✓ Fetched {len(df)} candles for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            print(f"✗ Error fetching data for {symbol} {timeframe}: {e}")
            return None
    
    def fetch_multiple_symbols(self, symbols: List[str], timeframe: str, limit: int = 500) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols
        
        Args:
            symbols: List of trading symbols
            timeframe: Timeframe to fetch
            limit: Number of candles per symbol
            
        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        results = {}
        
        print(f"Fetching data for {len(symbols)} symbols on {timeframe} timeframe...")
        
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Fetching {symbol}...")
            
            df = self.fetch_ohlcv(symbol, timeframe, limit)
            if df is not None:
                results[symbol] = df
            else:
                print(f"✗ Skipping {symbol} due to fetch error")
        
        print(f"✓ Successfully fetched data for {len(results)}/{len(symbols)} symbols")
        return results
    
    def fetch_all_timeframes(self, symbol: str, timeframes: List[str], limit: int = 500) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for a single symbol across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes to fetch
            limit: Number of candles per timeframe
            
        Returns:
            Dictionary mapping timeframes to their DataFrames
        """
        results = {}
        
        print(f"Fetching {symbol} data across {len(timeframes)} timeframes...")
        
        for i, timeframe in enumerate(timeframes, 1):
            print(f"[{i}/{len(timeframes)}] Fetching {symbol} {timeframe}...")
            
            df = self.fetch_ohlcv(symbol, timeframe, limit)
            if df is not None:
                results[timeframe] = df
            else:
                print(f"✗ Skipping {timeframe} for {symbol} due to fetch error")
        
        print(f"✓ Successfully fetched {symbol} data for {len(results)}/{len(timeframes)} timeframes")
        return results
    
    def get_market_info(self, symbol: str) -> Optional[Dict]:
        """Get market information for a symbol"""
        try:
            self._rate_limit_check()
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last_price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'change': ticker['change'],
                'percentage': ticker['percentage'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"✗ Error fetching market info for {symbol}: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is valid and tradeable"""
        try:
            self._rate_limit_check()
            markets = self.exchange.load_markets()
            return symbol in markets and markets[symbol]['active']
        except Exception as e:
            print(f"✗ Error validating symbol {symbol}: {e}")
            return False
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        try:
            markets = self.exchange.load_markets()
            return [symbol for symbol, market in markets.items() 
                   if market['active'] and market['type'] == 'spot']
        except Exception as e:
            print(f"✗ Error fetching available symbols: {e}")
            return []