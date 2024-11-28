from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.settings import OHLCT_COLUMN_POSITIONS as ohlct
from oandapysuite.objects.instrument import CandleCluster

from pandas import DataFrame, Series
import numpy as np

import ta
import talib


class PercentagePriceOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period_fast', 'period_slow']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'percentage_price_oscillator'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        percentage_price_oscillator = ta.momentum.PercentagePriceOscillator(close=datapoints, window_slow=self.period1, window_fast=self.period2, window_sign=self.signal)
        ppo = talib.PPO(
            datapoints,
            fastperiod=self.period1,
            slowperiod=self.period2,
        )
        setattr(self, 'x', time)
        setattr(self, 'y', ppo)



class RateOfChange(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'rate_of_change'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        roc = talib.ROC(
            datapoints,
            timeperiod=self.period
        )
        setattr(self, 'x', time)
        setattr(self, 'y', roc)

class RelativeStrengthIndex(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'relative_strength_index'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        rsi = talib.RSI(
            datapoints,
            timeperiod=self.period
        )
        setattr(self, 'x', time)
        setattr(self, 'y', rsi)

class StochasticOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period', 'smooth_window']
        self.fastk_period = 5
        self.slowk_period = 3
        self.slowk_matype = 0
        self.slowd_period = 3
        self.slowd_matype = 0
        super().__init__(**options)
        self.y_count = 2
        self.colors = {
            'y1': 'blue',
            'y2': 'red'
        }
        self.is_subplot = True
        self.indicator_id = 'stochastic_oscillator'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            highs = candle_cluster.candles[:, ohlct['high']].astype(np.float64)
            lows = candle_cluster.candles[:, ohlct['low']].astype(np.float64)
            closes = candle_cluster.candles[:, ohlct['close']].astype(np.float64)
            time = candle_cluster.candles[:, ohlct['time']].astype(np.float64)
        else:
            highs = candle_cluster[:, ohlct['high']].astype(np.float64)
            lows = candle_cluster[:, ohlct['low']].astype(np.float64)
            closes = candle_cluster[:, ohlct['close']].astype(np.float64)
            time = candle_cluster[:, ohlct['time']].astype(np.float64)
        slowk, slowd = talib.STOCH(
            high=highs,
            low=lows,
            close=closes,
            fastk_period=self.fastk_period,
            slowk_period=self.slowk_period,
            slowk_matype=self.slowk_matype,
            slowd_period=self.slowd_period,
            slowd_matype=self.slowd_matype
        )
        setattr(self, 'x', time)
        setattr(self, 'y1', slowk)
        setattr(self, 'y2', slowd)


class KAMA(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'kama'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        kama = talib.KAMA(
            datapoints,
            timeperiod=self.period
        )
        setattr(self, 'x', time)
        setattr(self, 'y', kama)

class StochasticRSI(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        self.fastk_period = 5
        self.fastd_period = 3
        self.fastd_maytype = 0
        super().__init__(**options)
        self.is_subplot = True
        self.y_count = 3
        self.indicator_id = 'stochastic_rsi'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        fastk, fastd = talib.STOCH(
            datapoints,
            fastk_period=self.fastk_period,
            fastd_period=self.fastd_period,
            fastd_matype=self.fastd_maytype,
            timeperiod=self.period
        )
        setattr(self, 'x', time)
        setattr(self, 'y1', fastk)
        setattr(self, 'y2', fastd)

class UltimateOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period1', 'period2', 'period3']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'ultimate_oscillator'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            highs = candle_cluster.candles[:, ohlct['high']].astype(np.float64)
            lows = candle_cluster.candles[:, ohlct['low']].astype(np.float64)
            closes = candle_cluster.candles[:, ohlct['close']].astype(np.float64)
            time = candle_cluster.candles[:, ohlct['time']].astype(np.float64)
        else:
            highs = candle_cluster[:, ohlct['high']].astype(np.float64)
            lows = candle_cluster[:, ohlct['low']].astype(np.float64)
            closes = candle_cluster[:, ohlct['close']].astype(np.float64)
            time = candle_cluster[:, ohlct['time']].astype(np.float64)
        ultosc = talib.ULTOSC(
            highs,
            lows,
            closes,
            timeperiod1=self.period1,
            timeperiod2=self.period2,
            timeperiod3=self.period3
        )
        setattr(self, 'x', time)
        setattr(self, 'y', ultosc)


class WilliamsR(BaseIndicator):

        def __init__(self, **options):
            self.required_options = ['period']
            super().__init__(**options)
            self.is_subplot = True
            self.indicator_id = 'williams_r'

        def update(self, candle_cluster):
            if type(candle_cluster) == CandleCluster:
                highs = candle_cluster.candles[:, ohlct['high']].astype(np.float64)
                lows = candle_cluster.candles[:, ohlct['low']].astype(np.float64)
                closes = candle_cluster.candles[:, ohlct['close']].astype(np.float64)
                time = candle_cluster.candles[:, ohlct['time']].astype(np.float64)
            else:
                highs = candle_cluster[:, ohlct['high']].astype(np.float64)
                lows = candle_cluster[:, ohlct['low']].astype(np.float64)
                closes = candle_cluster[:, ohlct['close']].astype(np.float64)
                time = candle_cluster[:, ohlct['time']].astype(np.float64)
            willr = talib.WILLR(
                highs,
                lows,
                closes,
                timeperiod=self.period
            )
            setattr(self, 'x', time)
            setattr(self, 'y', willr)