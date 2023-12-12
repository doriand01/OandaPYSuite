from oandapysuite.objects.indicators import BaseIndicator

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
            'candles' : candle_cluster.candles,
            'x'       : candle_cluster.history('time'),
            'y'       : simple_moving_average
        })
