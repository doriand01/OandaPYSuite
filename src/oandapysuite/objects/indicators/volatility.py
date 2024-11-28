from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite import utils
from oandapysuite.settings import OHLCT_COLUMN_POSITIONS as ohlct
from oandapysuite.objects.instrument import CandleCluster

from pandas import DataFrame, Series

import ta
import talib
import numpy as np
from numba import njit


class SampleStandardDeviation(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'sample_standard_deviation'

    def update(self, candle_cluster):
        self.is_subplot = True
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        standard_deviation = talib.STDDEV(datapoints.astype(np.float64), timeperiod=self.period)
        setattr(self, 'x', time)
        setattr(self, 'y', standard_deviation)


class BollingerBands(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period', 'std']
        self.y_count = 3
        super().__init__(**options)
        self.indicator_id = 'bollinger_bands'

    def is_up(self):
        return True if self.data.iloc[-1]['is_up'] else False

    def is_down(self):
        return True if self.data.iloc[-1]['is_down'] else False

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        upper, middle, lower = talib.BBANDS(datapoints.astype(np.float64), timeperiod=self.period, nbdevdn=self.std, nbdevup=self.std, matype=0)
        setattr(self, 'x', time)
        setattr(self, 'y1', lower)
        setattr(self, 'y2', upper)
        setattr(self, 'y3', middle)

class AverageTrueRange(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'average_true_range'

    @utils.run_as_thread
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
        atr = talib.ATR(high=highs, low=lows, close=closes, timeperiod=self.period)
        setattr(self, 'x', time)
        setattr(self, 'y', atr)

