from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite import utils
from oandapysuite.settings import OHLCT_COLUMN_POSITIONS as ohlct
from oandapysuite.objects.instrument import CandleCluster

from collections import deque

import ta
import talib
import numpy as np

from pandas import DataFrame, Series
from numba import njit


class SimpleMovingAverage(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'simple_moving_average'


    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        sma = talib.SMA(datapoints.astype(np.float64), timeperiod=self.period)
        setattr(self, 'x', time)
        setattr(self, 'y', sma)


    @utils.run_as_thread
    def update(self, candle_cluster):
        leg_range = self._find_legs(candle_cluster, self.lookback)
        for i in range(len(leg_range)):
            leg_range[i] = leg_range[i] + candle_cluster[i].close
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : leg_range
        })


class ExponentialMovingAverage(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'exponential_moving_average'

    @utils.run_as_thread
    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        ema = talib.EMA(datapoints.astype(np.float64), timeperiod=self.period)
        setattr(self, 'x', time)
        setattr(self, 'y', ema)


class TRIX(BaseIndicator):
    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'trix'

    def update(self, candle_cluster):
        if type(candle_cluster) == CandleCluster:
            datapoints = candle_cluster.candles[:, ohlct[self.on]]
            time = candle_cluster.candles[:, ohlct['time']]
        else:
            datapoints = candle_cluster[:, ohlct[self.on]]
            time = candle_cluster[:, ohlct['time']]
        trix = talib.TRIX(datapoints.astype(np.float64), timeperiod=self.period)
        setattr(self, 'x', time)
        setattr(self, 'y', trix)


class AverageDirectionalMovementIndex(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'average_directional_movement_index'

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
        adx = talib.ADXR(
            high=highs,
            low=lows,
            close=closes,
            timeperiod=self.period
        )
        setattr(self, 'x', time)
        setattr(self, 'y', adx)



class ParabolicSAR(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['accel', 'max']
        super().__init__(**options)
        self.is_subplot = False
        self.y_count = 2
        self.indicator_id = 'parabolic_sar'

    @utils.run_as_thread
    def update(self, candle_cluster):

        if type(candle_cluster) == CandleCluster:
            highs = candle_cluster.candles[:, ohlct['high']].astype(np.float64)
            lows = candle_cluster.candles[:, ohlct['low']].astype(np.float64)
            time = candle_cluster.candles[:, ohlct['time']].astype(np.float64)
        else:
            highs = candle_cluster[:, ohlct['high']].astype(np.float64)
            lows = candle_cluster[:, ohlct['low']].astype(np.float64)
            time = candle_cluster[:, ohlct['time']].astype(np.float64)
        psar = talib.SAR(
            highs=highs,
            lows=lows,
            acceleration=self.accel,
            maximum=self.max)
        setattr(self, 'x', time)
        setattr(self, 'y', psar)


class MovingAverageConvergenceDivergence(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period_fast', 'period_slow', 'period_signal']
        super().__init__(**options)
        self.is_subplot = True
        self.y_count = 3
        self.colors = {
            'y1' : 'red',
            'y2' : 'green',
            'y3' : 'blue'
        }
        self.indicator_id = 'moving_average_convergence_divergence'
        self.histogram = 'y3'

    def update(self, candle_cluster):

        datapoints = candle_cluster.history(self.on)
        macd, macdsignal, macdhist = talib.MACD(
            datapoints.astype(np.float64),
            fastperiod=self.period_fast,
            slowperiod=self.period_slow,
            signalperiod=self.period_signal
        )
        setattr(self, 'x', candle_cluster.history('time'))
        setattr(self, 'y1', macd)
        setattr(self, 'y2', macdsignal)
        setattr(self, 'y3', macdhist)

