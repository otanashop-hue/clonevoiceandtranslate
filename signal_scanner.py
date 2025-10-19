"""
Multi-symbol multi-timeframe signal scanner
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from vanguard_strategy import VanguardStrategy
from data_fetcher import DataFetcher
from config import SYMBOLS, TIMEFRAMES, SIGNAL_TYPES


class SignalScanner:
    """
    Scans multiple symbols and timeframes for trading signals
    """
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.strategy = VanguardStrategy()
        self.data_fetcher = DataFetcher()
        self.signals_history = []
        self.lock = threading.Lock()
        
    def scan_single_symbol_timeframe(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Scan a single symbol-timeframe combination for signals
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe to scan
            
        Returns:
            Signal information or None if no signal
        """
        try:
            # Fetch data
            df = self.data_fetcher.fetch_ohlcv(symbol, timeframe, limit=500)
            if df is None or len(df) < 200:
                return None
            
            # Get signal from strategy
            signal_type = self.strategy.f_vanguard(df)
            
            if signal_type == 5:  # NO_SIGNAL
                return None
            
            # Get current price and market info
            market_info = self.data_fetcher.get_market_info(symbol)
            current_price = market_info['last_price'] if market_info else df['close'].iloc[-1]
            
            # Create signal info
            signal_info = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'timeframe': timeframe,
                'signal_type': signal_type,
                'signal_name': SIGNAL_TYPES[signal_type],
                'current_price': current_price,
                'rsi': df['rsi'].iloc[-1] if 'rsi' in df.columns else None,
                'ema1': df['ema1'].iloc[-1] if 'ema1' in df.columns else None,
                'ema2': df['ema2'].iloc[-1] if 'ema2' in df.columns else None,
                'ema4': df['ema4'].iloc[-1] if 'ema4' in df.columns else None,
                'volume': df['volume'].iloc[-1] if 'volume' in df.columns else None,
                'market_info': market_info
            }
            
            return signal_info
            
        except Exception as e:
            print(f"✗ Error scanning {symbol} {timeframe}: {e}")
            return None
    
    def scan_symbol_all_timeframes(self, symbol: str, timeframes: List[str]) -> List[Dict]:
        """
        Scan a single symbol across all timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes to scan
            
        Returns:
            List of signals found
        """
        signals = []
        
        print(f"Scanning {symbol} across {len(timeframes)} timeframes...")
        
        for timeframe in timeframes:
            signal = self.scan_single_symbol_timeframe(symbol, timeframe)
            if signal:
                signals.append(signal)
                print(f"✓ Signal found: {symbol} {timeframe} - {signal['signal_name']}")
        
        return signals
    
    def scan_all_symbols_timeframe(self, symbols: List[str], timeframe: str) -> List[Dict]:
        """
        Scan all symbols on a single timeframe
        
        Args:
            symbols: List of trading symbols
            timeframe: Timeframe to scan
            
        Returns:
            List of signals found
        """
        signals = []
        
        print(f"Scanning {len(symbols)} symbols on {timeframe} timeframe...")
        
        for symbol in symbols:
            signal = self.scan_single_symbol_timeframe(symbol, timeframe)
            if signal:
                signals.append(signal)
                print(f"✓ Signal found: {symbol} {timeframe} - {signal['signal_name']}")
        
        return signals
    
    def scan_all_combinations(self, symbols: List[str], timeframes: List[str]) -> List[Dict]:
        """
        Scan all symbol-timeframe combinations
        
        Args:
            symbols: List of trading symbols
            timeframes: List of timeframes to scan
            
        Returns:
            List of all signals found
        """
        all_signals = []
        total_combinations = len(symbols) * len(timeframes)
        
        print(f"Starting comprehensive scan: {len(symbols)} symbols × {len(timeframes)} timeframes = {total_combinations} combinations")
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_combination = {}
            
            for symbol in symbols:
                for timeframe in timeframes:
                    future = executor.submit(self.scan_single_symbol_timeframe, symbol, timeframe)
                    future_to_combination[future] = (symbol, timeframe)
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_combination):
                symbol, timeframe = future_to_combination[future]
                completed += 1
                
                try:
                    signal = future.result()
                    if signal:
                        with self.lock:
                            all_signals.append(signal)
                        print(f"✓ [{completed}/{total_combinations}] Signal: {symbol} {timeframe} - {signal['signal_name']}")
                    else:
                        print(f"  [{completed}/{total_combinations}] No signal: {symbol} {timeframe}")
                        
                except Exception as e:
                    print(f"✗ [{completed}/{total_combinations}] Error: {symbol} {timeframe} - {e}")
        
        print(f"✓ Scan completed: {len(all_signals)} signals found out of {total_combinations} combinations")
        return all_signals
    
    def scan_priority_combinations(self, symbols: List[str], timeframes: List[str]) -> List[Dict]:
        """
        Scan with priority: first check all symbols on key timeframes, then others
        
        Args:
            symbols: List of trading symbols
            timeframes: List of timeframes to scan
            
        Returns:
            List of signals found
        """
        all_signals = []
        
        # Priority timeframes (shorter timeframes first for faster signals)
        priority_timeframes = ['1m', '3m', '5m', '15m', '30m']
        other_timeframes = [tf for tf in timeframes if tf not in priority_timeframes]
        
        print("Phase 1: Scanning priority timeframes...")
        for timeframe in priority_timeframes:
            if timeframe in timeframes:
                signals = self.scan_all_symbols_timeframe(symbols, timeframe)
                all_signals.extend(signals)
        
        print("Phase 2: Scanning remaining timeframes...")
        for timeframe in other_timeframes:
            signals = self.scan_all_symbols_timeframe(symbols, timeframe)
            all_signals.extend(signals)
        
        return all_signals
    
    def get_signal_summary(self, signals: List[Dict]) -> Dict:
        """
        Get summary statistics for signals
        
        Args:
            signals: List of signals
            
        Returns:
            Summary statistics
        """
        if not signals:
            return {
                'total_signals': 0,
                'by_signal_type': {},
                'by_symbol': {},
                'by_timeframe': {},
                'buy_signals': 0,
                'sell_signals': 0
            }
        
        summary = {
            'total_signals': len(signals),
            'by_signal_type': {},
            'by_symbol': {},
            'by_timeframe': {},
            'buy_signals': 0,
            'sell_signals': 0
        }
        
        for signal in signals:
            # Count by signal type
            signal_type = signal['signal_name']
            summary['by_signal_type'][signal_type] = summary['by_signal_type'].get(signal_type, 0) + 1
            
            # Count by symbol
            symbol = signal['symbol']
            summary['by_symbol'][symbol] = summary['by_symbol'].get(symbol, 0) + 1
            
            # Count by timeframe
            timeframe = signal['timeframe']
            summary['by_timeframe'][timeframe] = summary['by_timeframe'].get(timeframe, 0) + 1
            
            # Count buy vs sell
            if 'BUY' in signal_type:
                summary['buy_signals'] += 1
            elif 'SELL' in signal_type:
                summary['sell_signals'] += 1
        
        return summary
    
    def save_signals_to_file(self, signals: List[Dict], filename: str = None):
        """
        Save signals to a CSV file
        
        Args:
            signals: List of signals to save
            filename: Output filename (optional)
        """
        if not signals:
            print("No signals to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"signals_{timestamp}.csv"
        
        # Convert to DataFrame
        df = pd.DataFrame(signals)
        
        # Flatten market_info if present
        if 'market_info' in df.columns:
            market_cols = ['last_price', 'bid', 'ask', 'volume', 'change', 'percentage']
            for col in market_cols:
                df[f'market_{col}'] = df['market_info'].apply(
                    lambda x: x.get(col, None) if isinstance(x, dict) else None
                )
            df.drop('market_info', axis=1, inplace=True)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"✓ Saved {len(signals)} signals to {filename}")
    
    def add_to_history(self, signals: List[Dict]):
        """Add signals to history for tracking"""
        with self.lock:
            self.signals_history.extend(signals)
    
    def get_recent_signals(self, minutes: int = 60) -> List[Dict]:
        """Get signals from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [s for s in self.signals_history if s['timestamp'] > cutoff_time]