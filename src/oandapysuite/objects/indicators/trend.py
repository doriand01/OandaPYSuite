from oandapysuite.objects.indicators import BaseIndicator

import ta

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


class ExponentialMovingAverage(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'exponential_moving_average'

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
        self.indicator_id = 'parabolic_sar'

    def is_psar_up(self):
        return True if self.data['is_psar_up'].iloc[-1] else False

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
        self.indicator_id = 'moving_average_convergence_divergence'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        moving_average_convergence_divergence = ta.trend.MACD(close=datapoints, window_slow=self.period_slow, window_fast=self.period_fast, window_sign=self.period_signal)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : moving_average_convergence_divergence.macd(),
            'y2'      : moving_average_convergence_divergence.macd_signal(),
            'y3'      : moving_average_convergence_divergence.macd_diff()
        })