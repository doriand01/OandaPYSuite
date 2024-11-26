from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite import utils

from pandas import DataFrame, Series

import ta


class SampleStandardDeviation(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'sample_standard_deviation'

    def update(self, candle_cluster):
        self.is_subplot = True
        datapoints = candle_cluster.history(self.on)
        standard_deviation = datapoints.rolling(self.period).std()
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : standard_deviation
        })


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
        datapoints = candle_cluster.history(self.on)
        boll_bands = ta.volatility.BollingerBands(close=datapoints, window=self.period, window_dev=self.std)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'      : boll_bands.bollinger_lband(),
            'y2'      : boll_bands.bollinger_hband(),
            'y3'      : boll_bands.bollinger_mavg(),
            'is_up'   : boll_bands.bollinger_hband_indicator(),
            'is_down' : boll_bands.bollinger_lband_indicator(),
        })


class KeltnerChannels(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.y_count = 3
        self.indicator_id = 'keltner_channels'

    def is_up(self):
        return True if self.data.iloc[-1]['is_up'] else False

    def is_down(self):
        return True if self.data.iloc[-1]['is_down'] else False

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        keltner_channels = ta.volatility.KeltnerChannel(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'      : keltner_channels.keltner_channel_lband(),
            'y2'      : keltner_channels.keltner_channel_hband(),
            'y3'      : keltner_channels.keltner_channel_mband(),
            'is_up'   : keltner_channels.keltner_channel_hband_indicator(),
            'is_down' : keltner_channels.keltner_channel_lband_indicator(),
        })


class UlcerIndex(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'ulcer_index'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        ulcer_index = ta.volatility.UlcerIndex(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : ulcer_index.ulcer_index(),
        })
        self.indicator_id = 'ulcer_index'


class AverageTrueRange(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'average_true_range'

    @utils.run_as_thread
    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        average_true_range = ta.volatility.AverageTrueRange(high=highs, low=lows, close=closes, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : average_true_range.average_true_range(),
        })
        self.indicator_id = 'average_true_range'


class DonchianChannel(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period']
        super().__init__(**options)
        self.is_subplot = True
        self.y_count = 3
        self.indicator_id = 'donchian_channel'

    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        donchian_channel = ta.volatility.DonchianChannel(high=highs, low=lows, close=closes, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : donchian_channel.donchian_channel_lband(),
            'y2'       : donchian_channel.donchian_channel_mband(),
            'y3'       : donchian_channel.donchian_channel_hband(),
        })
        self.indicator_id = 'donchian_channel'


class ZScoreOfPrice(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'z_score_of_price'

    @staticmethod
    def __calculate_zscore(rolling_window):
        zscore = (rolling_window.iloc[-1] - rolling_window.mean()) / rolling_window.std()
        return zscore

    @utils.run_as_thread
    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        window = datapoints.rolling(self.period)
        zscore = window.apply(self.__calculate_zscore)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : zscore
        })


class AverageDifference(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.indicator_id = 'average_difference'

    @staticmethod
    def __calculate_average_difference(rolling_window):
        differences = rolling_window.sub(rolling_window.iloc[-1])
        avg_diff = differences.mean()
        return avg_diff

    def update(self, candle_cluster):
        self.is_subplot = True
        window = candle_cluster.history(self.on).rolling(self.period, min_periods=self.period)
        average_differences = window.apply(self.__calculate_average_difference)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : average_differences
        })
