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
        self.y_count = 3
        self.indicator_id = 'percentage_price_oscillator'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        percentage_price_oscillator = ta.momentum.PercentagePriceOscillator(close=datapoints, window_slow=self.period1, window_fast=self.period2, window_sign=self.signal)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : percentage_price_oscillator.ppo(),
            'y2'      : percentage_price_oscillator.ppo_signal(),
            'y3'      : percentage_price_oscillator.ppo_hist()
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


class KAMA(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period1', 'period2', 'period3']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'kama'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        kama = ta.momentum.KAMAIndicator(close=datapoints, window=self.period1, pow1=self.period2, pow2=self.period3)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : kama.kama()
        })

class StochasticRSI(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['on', 'period', 'smooth1', 'smooth2']
        super().__init__(**options)
        self.is_subplot = True
        self.y_count = 3
        self.indicator_id = 'stochastic_rsi'

    def update(self, candle_cluster):
        datapoints = candle_cluster.history(self.on)
        stochastic_rsi = ta.momentum.StochasticRSIIndicator(close=datapoints, window=self.period, smooth1=self.smooth1, smooth2=self.smooth2)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y1'       : stochastic_rsi.stochrsi(),
            'y2'       : stochastic_rsi.stochrsi_d(),
            'y3'       : stochastic_rsi.stochrsi_k()
        })

class UltimateOscillator(BaseIndicator):

    def __init__(self, **options):
        self.required_options = ['period1', 'period2', 'period3', 'weight1', 'weight2', 'weight3']
        super().__init__(**options)
        self.is_subplot = True
        self.indicator_id = 'ultimate_oscillator'

    def update(self, candle_cluster):
        highs = candle_cluster.history('high')
        lows = candle_cluster.history('low')
        closes = candle_cluster.history('close')
        ultimate_oscillator = ta.momentum.UltimateOscillator(
            high=highs, low=lows, close=closes,
            window1=self.period1, window2=self.period2,
            window3=self.period3, weight1=self.weight1,
            weight2=self.weight2, weight3=self.weight3)
        self.data = DataFrame(data={
            'x'       : candle_cluster.history('time'),
            'y'       : ultimate_oscillator.ultimate_oscillator()
        })


class WilliamsR(BaseIndicator):

        def __init__(self, **options):
            self.required_options = ['period']
            super().__init__(**options)
            self.is_subplot = True
            self.indicator_id = 'williams_r'

        def update(self, candle_cluster):
            highs = candle_cluster.history('high')
            lows = candle_cluster.history('low')
            closes = candle_cluster.history('close')
            williams_r = ta.momentum.WilliamsRIndicator(high=highs, low=lows, close=closes, lbp=self.period)
            self.data = DataFrame(data={
                'x'       : candle_cluster.history('time'),
                'y'       : williams_r.williams_r()
            })