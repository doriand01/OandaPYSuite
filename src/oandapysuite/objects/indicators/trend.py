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

    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        parabolic_sar = ta.trend.PSARIndicator(high=highs, low=lows, close=closes, step=self.accel, max_step=self.max)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : parabolic_sar.psar_down(),
            'y2'       : parabolic_sar.psar_up()
        })
