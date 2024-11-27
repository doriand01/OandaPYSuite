from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite import utils

from collections import deque

import ta
import numpy as np

from pandas import DataFrame, Series


class SimpleMovingAverage(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'simple_moving_average'


    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        simple_moving_average = datapoints.rolling(self.period).mean()
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : simple_moving_average
        })

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
        datapoints = candle_cluster.history(self.on)
        exponential_moving_average = ta.trend.EMAIndicator(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : exponential_moving_average.ema_indicator()
        })


class TRIX(BaseIndicator):
    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'trix'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        trix = ta.trend.TRIXIndicator(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : trix.trix()
        })


class AverageDirectionalMovementIndex(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'average_directional_movement_index'

    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        adx = ta.trend.ADXIndicator(high=highs, low=lows, close=closes, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : adx.adx()
        })


class ParabolicSAR(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['accel', 'max']
        super().__init__(**options)
        self.is_subplot = False
        self.y_count = 2
        self.colors = {
            'y1' : 'red',
            'y2' : 'green'
        }
        self.indicator_id = 'parabolic_sar'

    def is_psar_up(self):
        return True if self.data['is_psar_up'].iloc[-1] else False

    @utils.run_as_thread
    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        parabolic_sar = ta.trend.PSARIndicator(high=highs, low=lows, close=closes, step=self.accel, max_step=self.max)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : parabolic_sar.psar_down(),
            'y2'       : parabolic_sar.psar_up(),
            'is_psar_up' : parabolic_sar.psar_up_indicator(),
            'is_psar_down' : parabolic_sar.psar_down_indicator()
        })


class DetrendedPriceOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'detrended_price_oscillator'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        detrended_price_oscillator = ta.trend.DPOIndicator(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : detrended_price_oscillator.dpo()
        })


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
        moving_average_convergence_divergence = ta.trend.MACD(
            close=datapoints, window_slow=self.period_slow,
            window_fast=self.period_fast, window_sign=self.period_signal)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'      : moving_average_convergence_divergence.macd(),
            'y2'      : moving_average_convergence_divergence.macd_signal(),
            'y3'      : moving_average_convergence_divergence.macd_diff()
        })


class TrendlineLinearRegression(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'window_size', 'order']
        super().__init__(**options)
        self.y_count = 2
        self.colors = {
            'y1' : 'green',
            'y2' : 'red',
        }
        self.indicator_id = 'trendline_linear_regression'

    def update(self, candle_cluster):
        window_index = 0
        y1 = []
        y2 = []
        window_upper_bounds = ([],[])
        window_lower_bounds = ([],[])
        for i in range(len(candle_cluster)):
            if window_index - self.order < 0:
                window_index += 1
                continue
            elif window_index + self.order >= self.window_size or i + self.order >= len(candle_cluster):
                y1m, y1b = np.polyfit(window_upper_bounds[0], window_upper_bounds[1], 1)
                y2m, y2b = np.polyfit(window_lower_bounds[0], window_lower_bounds[1], 1)
                window1_y = [y1m * x + y1b for x in range(self.window_size)]
                window2_y = [y2m * x + y2b for x in range(self.window_size)]
                y1 = y1 + window1_y
                y2 = y2 + window2_y
                window_upper_bounds = ([], [])
                window_lower_bounds = ([], [])
                window_index = 0
                continue
            elif len(y1) == len(candle_cluster):
                break
            else:
                window = candle_cluster.candles[i - self.order:i + self.order]
                if all([candle_cluster[i].close >= candle.close for candle in window]):
                    window_upper_bounds[0].append(window_index)
                    window_upper_bounds[1].append(float(candle_cluster[i].close))
                elif all([candle_cluster[i].close <= candle.close for candle in window]):
                    window_lower_bounds[0].append(window_index)
                    window_lower_bounds[1].append(float(candle_cluster[i].close))
                window_index += 1

        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : y1,
            'y2'       : y2
        })