"""
Vanguard Trading Strategy Implementation
Based on the provided f_Vanguard() function
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Tuple, Optional
from config import VANGUARD_PARAMS


class VanguardStrategy:
    """
    Implementation of the Vanguard trading strategy
    """
    
    def __init__(self, params: Dict = None):
        self.params = params or VANGUARD_PARAMS
        self.ema_periods = self.params["ema_periods"]
        self.rsi_period = self.params["rsi_period"]
        self.rsi_low = self.params["rsi_low"]
        self.rsi_high = self.params["rsi_high"]
        self.rsi_low2 = self.params["rsi_low2"]
        self.rsi_high2 = self.params["rsi_high2"]
        self.cci_period = self.params["cci_period"]
        self.cci_low = self.params["cci_low"]
        self.cci_high = self.params["cci_high"]
        self.iscci = self.params["iscci"]
        self.iswvap = self.params["iswvap"]
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required technical indicators"""
        df = df.copy()
        
        # Calculate EMAs
        df['ema1'] = ta.trend.EMAIndicator(close=df['hl2'], window=self.ema_periods[0]).ema_indicator()
        df['ema2'] = ta.trend.EMAIndicator(close=df['hl2'], window=self.ema_periods[1]).ema_indicator()
        df['ema3'] = ta.trend.EMAIndicator(close=df['hl2'], window=self.ema_periods[2]).ema_indicator()
        df['ema4'] = ta.trend.EMAIndicator(close=df['hl2'], window=self.ema_periods[3]).ema_indicator()
        
        # Calculate RSI
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=self.rsi_period).rsi()
        
        # Calculate CCI
        df['cci'] = ta.trend.CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=self.cci_period).cci()
        
        # Calculate VWAP (using daily anchor)
        df['vwap'] = ta.volume.VolumeSMAIndicator(close=df['hlc3'], volume=df['volume']).volume_sma()
        
        # Calculate pivot points
        df['pll'] = self._calculate_pivot_low(df['rsi'], 2, 2)
        df['phh'] = self._calculate_pivot_high(df['rsi'], 2, 2)
        
        return df
    
    def _calculate_pivot_low(self, series: pd.Series, left: int, right: int) -> pd.Series:
        """Calculate pivot low points"""
        result = pd.Series(index=series.index, dtype=float)
        for i in range(left, len(series) - right):
            if all(series.iloc[i] < series.iloc[i-j] for j in range(1, left+1)) and \
               all(series.iloc[i] < series.iloc[i+j] for j in range(1, right+1)):
                result.iloc[i] = series.iloc[i]
        return result
    
    def _calculate_pivot_high(self, series: pd.Series, left: int, right: int) -> pd.Series:
        """Calculate pivot high points"""
        result = pd.Series(index=series.index, dtype=float)
        for i in range(left, len(series) - right):
            if all(series.iloc[i] > series.iloc[i-j] for j in range(1, left+1)) and \
               all(series.iloc[i] > series.iloc[i+j] for j in range(1, right+1)):
                result.iloc[i] = series.iloc[i]
        return result
    
    def f_vanguard(self, df: pd.DataFrame) -> int:
        """
        Main Vanguard function that returns signal type
        Returns: 1=BUY_30, 2=SELL_30, 3=BUY_60, 4=SELL_60, 5=NO_SIGNAL
        """
        if len(df) < 200:  # Need enough data for calculations
            return 5
        
        df = self.calculate_indicators(df)
        
        # Get latest values
        latest = df.iloc[-1]
        prev_data = df.iloc[:-1]
        
        # Find RSI overbought conditions
        rsiob = False
        rsiobnum = 0
        for i in range(len(prev_data)):
            if not pd.isna(prev_data['pll'].iloc[i]):
                for j in range(i + 2):
                    if prev_data['rsi'].iloc[j] >= 70:
                        rsiob = True
                        rsiobnum = j
                        break
                if rsiob:
                    break
        
        # Find RSI oversold conditions
        rsiob2 = False
        rsiobnum2 = 0
        for i in range(len(prev_data)):
            if not pd.isna(prev_data['phh'].iloc[i]):
                for j in range(i + 2):
                    if prev_data['rsi'].iloc[j] <= 30:
                        rsiob2 = True
                        rsiobnum2 = j
                        break
                if rsiob2:
                    break
        
        # Calculate buy signals
        buy_signal = self._calculate_buy_signal(df, rsiob, rsiobnum)
        buy60_signal = self._calculate_buy60_signal(df, rsiob, rsiobnum)
        
        # Calculate sell signals
        sell_signal = self._calculate_sell_signal(df, rsiob2, rsiobnum2)
        sell60_signal = self._calculate_sell60_signal(df, rsiob2, rsiobnum2)
        
        # Return signal priority
        if buy_signal:
            return 1  # BUY_30
        elif sell_signal:
            return 2  # SELL_30
        elif buy60_signal:
            return 3  # BUY_60
        elif sell60_signal:
            return 4  # SELL_60
        else:
            return 5  # NO_SIGNAL
    
    def _calculate_buy_signal(self, df: pd.DataFrame, rsiob: bool, rsiobnum: int) -> bool:
        """Calculate BUY_30 signal"""
        if not rsiob or rsiobnum == 0:
            return False
        
        latest = df.iloc[-1]
        prev_data = df.iloc[:-1]
        
        # Find first touch of EMA1
        firsttoch = -1
        for i in range(rsiobnum + 1):
            if prev_data['low'].iloc[i] < prev_data['ema1'].iloc[i]:
                firsttoch = i
                break
        
        if firsttoch < 0:
            return False
        
        # Check for no green candles before touch
        nogreencandle = False
        for i in range(1, firsttoch + 1):
            if prev_data['close'].iloc[i] > prev_data['open'].iloc[i]:
                nogreencandle = True
                break
        
        # Check touch conditions
        tochema30 = (
            (prev_data['low'].iloc[firsttoch] < prev_data['ema1'].iloc[firsttoch] and 
             prev_data['close'].iloc[firsttoch] > prev_data['open'].iloc[firsttoch] and 
             firsttoch == 0) or
            (prev_data['low'].iloc[firsttoch] < prev_data['ema1'].iloc[firsttoch] and 
             not nogreencandle and 
             latest['close'] > latest['ema1'] and 
             latest['close'] > latest['open'] and 
             firsttoch >= 0)
        )
        
        if not tochema30:
            return False
        
        # Additional conditions
        base2rsinum = firsttoch if (firsttoch == 0 and prev_data['close'].iloc[firsttoch] > prev_data['open'].iloc[firsttoch]) else firsttoch + 1
        base2rsi = prev_data['rsi'].iloc[base2rsinum]
        
        # Find minimum RSI
        for i in range(base2rsinum, rsiobnum + 1):
            if prev_data['rsi'].iloc[i] < base2rsi:
                base2rsi = prev_data['rsi'].iloc[i]
        
        # Check RSI conditions
        rsi_above_rsilow = all(prev_data['rsi'].iloc[i] >= self.rsi_low for i in range(rsiobnum + 1))
        
        # Find pivot low number
        plnum = 0
        for i in range(rsiobnum, min(rsiobnum + 100, len(prev_data))):
            if not pd.isna(prev_data['pll'].iloc[i]):
                if (rsiob and 
                    self.rsi_low <= prev_data['rsi'].iloc[i+2] <= self.rsi_high):
                    plnum = i + 2
                    break
        
        # Final buy conditions
        return (
            firsttoch >= 0 and
            base2rsi < prev_data['rsi'].iloc[plnum] and
            plnum > 0 and
            tochema30 and
            latest['ema2'] > latest['ema4'] and
            prev_data['low'].iloc[base2rsinum] > prev_data['low'].iloc[plnum] and
            latest['rsi'] > self.rsi_low and
            rsi_above_rsilow
        )
    
    def _calculate_buy60_signal(self, df: pd.DataFrame, rsiob: bool, rsiobnum: int) -> bool:
        """Calculate BUY_60 signal"""
        if not rsiob or rsiobnum == 0:
            return False
        
        latest = df.iloc[-1]
        prev_data = df.iloc[:-1]
        
        # Find first touch of EMA2
        firsttoch60 = -1
        for i in range(rsiobnum + 1):
            if prev_data['low'].iloc[i] < prev_data['ema2'].iloc[i]:
                firsttoch60 = i
                break
        
        if firsttoch60 < 0:
            return False
        
        # Similar logic as BUY_30 but with EMA2
        nogreencandle60 = False
        for i in range(1, firsttoch60 + 1):
            if prev_data['close'].iloc[i] > prev_data['open'].iloc[i]:
                nogreencandle60 = True
                break
        
        tochema60 = (
            (prev_data['low'].iloc[firsttoch60] < prev_data['ema2'].iloc[firsttoch60] and 
             prev_data['close'].iloc[firsttoch60] > prev_data['open'].iloc[firsttoch60] and 
             firsttoch60 == 0) or
            (prev_data['low'].iloc[firsttoch60] < prev_data['ema2'].iloc[firsttoch60] and 
             not nogreencandle60 and 
             latest['close'] > latest['ema2'] and 
             latest['close'] > latest['open'] and 
             firsttoch60 >= 0)
        )
        
        if not tochema60:
            return False
        
        # Additional conditions similar to BUY_30
        base2rsinum60 = firsttoch60 if (firsttoch60 == 0 and prev_data['close'].iloc[firsttoch60] > prev_data['open'].iloc[firsttoch60]) else firsttoch60 + 1
        base2rsi60 = prev_data['rsi'].iloc[base2rsinum60]
        
        for i in range(base2rsinum60, rsiobnum + 1):
            if prev_data['rsi'].iloc[i] < base2rsi60:
                base2rsi60 = prev_data['rsi'].iloc[i]
        
        rsi_above_rsilow60 = all(prev_data['rsi'].iloc[i] >= self.rsi_low for i in range(rsiobnum + 1))
        
        plnum = 0
        for i in range(rsiobnum, min(rsiobnum + 100, len(prev_data))):
            if not pd.isna(prev_data['pll'].iloc[i]):
                if (rsiob and 
                    self.rsi_low <= prev_data['rsi'].iloc[i+2] <= self.rsi_high):
                    plnum = i + 2
                    break
        
        return (
            firsttoch60 >= 0 and
            base2rsi60 < prev_data['rsi'].iloc[plnum] and
            plnum > 0 and
            tochema60 and
            latest['ema2'] > latest['ema4'] and
            prev_data['low'].iloc[base2rsinum60] > prev_data['low'].iloc[plnum] and
            latest['rsi'] > self.rsi_low and
            rsi_above_rsilow60
        )
    
    def _calculate_sell_signal(self, df: pd.DataFrame, rsiob2: bool, rsiobnum2: int) -> bool:
        """Calculate SELL_30 signal"""
        if not rsiob2 or rsiobnum2 == 0:
            return False
        
        latest = df.iloc[-1]
        prev_data = df.iloc[:-1]
        
        # Find first touch of EMA1 (for sell)
        firsttoch30_2 = -1
        for i in range(rsiobnum2 + 1):
            if prev_data['high'].iloc[i] > prev_data['ema1'].iloc[i]:
                firsttoch30_2 = i
                break
        
        if firsttoch30_2 < 0:
            return False
        
        # Check for no red candles before touch
        nogreencandle2 = False
        for i in range(1, firsttoch30_2 + 1):
            if prev_data['close'].iloc[i] < prev_data['open'].iloc[i]:
                nogreencandle2 = True
                break
        
        # Check touch conditions for sell
        tochema30_2 = (
            (prev_data['high'].iloc[firsttoch30_2] > prev_data['ema1'].iloc[firsttoch30_2] and 
             prev_data['close'].iloc[firsttoch30_2] < prev_data['open'].iloc[firsttoch30_2] and 
             firsttoch30_2 == 0) or
            (prev_data['high'].iloc[firsttoch30_2] > prev_data['ema1'].iloc[firsttoch30_2] and 
             not nogreencandle2 and 
             latest['close'] < latest['ema1'] and 
             latest['close'] < latest['open'] and 
             firsttoch30_2 >= 0)
        )
        
        if not tochema30_2:
            return False
        
        # Additional sell conditions
        base2rsinum2 = firsttoch30_2 if (firsttoch30_2 == 0 and prev_data['close'].iloc[firsttoch30_2] < prev_data['open'].iloc[firsttoch30_2]) else firsttoch30_2 + 1
        base2rsi2 = prev_data['rsi'].iloc[base2rsinum2]
        
        for i in range(base2rsinum2, rsiobnum2 + 1):
            if prev_data['rsi'].iloc[i] > base2rsi2:
                base2rsi2 = prev_data['rsi'].iloc[i]
        
        rsi_above_rsihigh = all(prev_data['rsi'].iloc[i] <= self.rsi_high2 for i in range(rsiobnum2 + 1))
        
        phnum = 0
        for i in range(rsiobnum2, min(rsiobnum2 + 100, len(prev_data))):
            if not pd.isna(prev_data['phh'].iloc[i]):
                if (rsiob2 and 
                    self.rsi_low2 <= prev_data['rsi'].iloc[i+2] <= self.rsi_high2):
                    phnum = i + 2
                    break
        
        return (
            firsttoch30_2 >= 0 and
            base2rsi2 > prev_data['rsi'].iloc[phnum] and
            phnum > 0 and
            tochema30_2 and
            latest['ema2'] < latest['ema4'] and
            prev_data['high'].iloc[base2rsinum2] < prev_data['high'].iloc[phnum] and
            latest['rsi'] < self.rsi_high2 and
            rsi_above_rsihigh
        )
    
    def _calculate_sell60_signal(self, df: pd.DataFrame, rsiob2: bool, rsiobnum2: int) -> bool:
        """Calculate SELL_60 signal"""
        if not rsiob2 or rsiobnum2 == 0:
            return False
        
        latest = df.iloc[-1]
        prev_data = df.iloc[:-1]
        
        # Find first touch of EMA2 (for sell)
        firsttoch602 = -1
        for i in range(rsiobnum2 + 1):
            if prev_data['high'].iloc[i] > prev_data['ema2'].iloc[i]:
                firsttoch602 = i
                break
        
        if firsttoch602 < 0:
            return False
        
        # Similar logic as SELL_30 but with EMA2
        nogreencandle602 = False
        for i in range(1, firsttoch602 + 1):
            if prev_data['close'].iloc[i] < prev_data['open'].iloc[i]:
                nogreencandle602 = True
                break
        
        tochema602 = (
            (prev_data['high'].iloc[firsttoch602] > prev_data['ema2'].iloc[firsttoch602] and 
             prev_data['close'].iloc[firsttoch602] < prev_data['open'].iloc[firsttoch602] and 
             firsttoch602 == 0) or
            (prev_data['high'].iloc[firsttoch602] > prev_data['ema2'].iloc[firsttoch602] and 
             not nogreencandle602 and 
             latest['close'] < latest['ema2'] and 
             latest['close'] < latest['open'] and 
             firsttoch602 >= 0)
        )
        
        if not tochema602:
            return False
        
        # Additional conditions similar to SELL_30
        base2rsinum602 = firsttoch602 if (firsttoch602 == 0 and prev_data['close'].iloc[firsttoch602] < prev_data['open'].iloc[firsttoch602]) else firsttoch602 + 1
        base2rsi602 = prev_data['rsi'].iloc[base2rsinum602]
        
        for i in range(base2rsinum602, rsiobnum2 + 1):
            if prev_data['rsi'].iloc[i] > base2rsi602:
                base2rsi602 = prev_data['rsi'].iloc[i]
        
        rsi_above_rsihigh60 = all(prev_data['rsi'].iloc[i] <= self.rsi_high2 for i in range(rsiobnum2 + 1))
        
        phnum = 0
        for i in range(rsiobnum2, min(rsiobnum2 + 100, len(prev_data))):
            if not pd.isna(prev_data['phh'].iloc[i]):
                if (rsiob2 and 
                    self.rsi_low2 <= prev_data['rsi'].iloc[i+2] <= self.rsi_high2):
                    phnum = i + 2
                    break
        
        return (
            firsttoch602 >= 0 and
            base2rsi602 > prev_data['rsi'].iloc[phnum] and
            phnum > 0 and
            tochema602 and
            latest['ema2'] < latest['ema4'] and
            prev_data['high'].iloc[base2rsinum602] < prev_data['high'].iloc[phnum] and
            latest['rsi'] < self.rsi_high2 and
            rsi_above_rsihigh60
        )