from oandapysuite.objects.indicators import BaseIndicator

from pandas import DataFrame, Series

import ta


class AwesomeOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['high', 'low', 'period1', 'period2']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'awesome_oscillator'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        awesome_oscillator = ta.momentum.AwesomeOscillatorIndicator(high=datapoints['high'], low=datapoints['low'], window1=self.period1, window2=self.period2)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : awesome_oscillator.awesome_oscillator()
        })


class PercentagePriceOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period1', 'period2', 'signal']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'percentage_price_oscillator'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        percentage_price_oscillator = ta.momentum.PercentagePriceOscillator(close=datapoints, window_slow=self.period1, window_fast=self.period2, window_sign=self.signal)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : percentage_price_oscillator.ppo()
        })


class RateOfChange(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'rate_of_change'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        rate_of_change = ta.momentum.ROCIndicator(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : rate_of_change.roc()
        })

class RelativeStrengthIndex(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'relative_strength_index'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        relative_strength_index = ta.momentum.RSIIndicator(close=datapoints, window=self.period)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : relative_strength_index.rsi()
        })

class StochasticOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period', 'smooth_window']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'stochastic_oscillator'

    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        stochastic_oscillator = ta.momentum.StochasticOscillator(high=highs, low=lows, close=closes, window=self.period, smooth_window=self.smooth_window)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : stochastic_oscillator.stoch()
        })


class TrueStrengthIndex(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period1', 'period2']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'true_strength_index'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        true_strength_index = ta.momentum.TSIIndicator(close=datapoints, window_slow=self.period1, window_fast=self.period2)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : true_strength_index.tsi()
        })