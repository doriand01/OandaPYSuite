from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.exceptions import IndicatorOptionsError

import math
import decimal

import numpy as np
from pandas import DataFrame, Series



D = decimal.Decimal

decimal.getcontext().prec = 6

class BaseIndicator:
    """
    BaseIndicator is the class that all other indicators inherit from. It allows functions to be defined
    that take CandleCluster objects as paramaters to create a data point for the specified time range of
    candles. These can indicators can then be added to the chart and rendered using the API.
    To create a custom indicator, your indicator class must inherit from the BaseIndicator class, and it must
    override the `BaseIndicator.ind_algorithm() function. This function takes one parameter (besides self) as
    an argument, which is the CandleCluster object. Here in this function, you can run your statistics over
    the data to calculate the values for your indicators, however, the ind_algorithm function must return a pandas
    dataframe with at least two columns, one for the x-axis (time) for each data point, and the others with your data.
    """

    def add_candle(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        return None

    def __init__(self, **options):
        """
        __init__(
            self,
            options: dict(), <--- Parameters for your indicator. eg. period, etc...
            )
        """
        self.candles_dict = {}
        self.data_dict = {
            'candles' : [],
            'x' : [],
            'y' : []
        }
        if 'on' in options:
            self.period = options['on']
        for key, value in options.items():
            setattr(self, key, value)
        self.is_subplot = False
        self.multi_y = False
        self.options = options
        self.data = DataFrame(
                data={
                    'candles' : [],
                    'x'       : [],
                    'y'       : []
                }
            )


class SimpleMovingAverage(BaseIndicator):

    def add_candle(self, candle):
        data_size = len(self.candles_dict.values())
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            period_sum = sum(
                    [getattr(list(self.candles_dict.values())[j], self.options['on']) for j in range(
                        data_size - self.period, data_size
                    )]
                )
            period_avg = period_sum / self.period
            self.data_dict['y'].append(period_avg)
            self.data_dict['candles'].append(candle)
        self.data = DataFrame(data=self.data_dict)


class SampleStandardDeviation(BaseIndicator):

    def __init__(self, **options):
        super().__init__(**options)
        self.indicator_id = 'sample_standard_deviation'

    def add_candle(self, candle):
        self.is_subplot = True
        data_size = len(self.candles_dict.values())
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            self.period_avg = sum(
                    [getattr(list(self.candles_dict.values())[j], self.options['on']) for j in range(
                        data_size - self.period, data_size
                    )]
                ) / self.period
            period_diff_sum = sum(
                    [(getattr(list(self.candles_dict.values())[j], self.options['on']) - self.period_avg) ** 2 for j in range(
                        data_size - self.period, data_size
                    )]
                )
            period_std = decimal.Decimal(math.sqrt(period_diff_sum / self.period))
            self.data_dict['y'].append(period_std)
            self.data_dict['candles'].append(candle)
        self.data = DataFrame(data=self.data_dict)

class BollingerBands(BaseIndicator):

    def __init__(self, std_indicator, **options):
        super().__init__(**options)
        self.data_dict['y1'] = []
        self.data_dict['y2'] = []
        self.std_indicator = std_indicator
        self.indicator_id = 'bollinger_bands'
        self.multi_y = True

    def add_candle(self, candle):
        self.std_indicator.add_candle(candle)
        data_size = len(self.candles_dict.values())
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['y1'].append(None)
            self.data_dict['y2'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            period_std = self.std_indicator.data.iloc[-1]['y']
            period_avg = sum(
                    [getattr(list(self.candles_dict.values())[j], self.options['on']) for j in range(
                        data_size - self.period, data_size
                    )]
                ) / self.period
            upper_band = period_avg + period_std * 2
            lower_band = period_avg - period_std * 2
            self.data_dict['y'].append(upper_band)
            self.data_dict['y1'].append(period_avg)
            self.data_dict['y2'].append(lower_band)
            self.data_dict['candles'].append(candle)
        self.data = DataFrame(data=self.data_dict)


class ZScoreOfPrice(BaseIndicator):

    def __init__(self, std_indicator, **options):
        super().__init__(options)
        self.std_indicator = std_indicator
        self.indicator_id = 'z_score_of_price'

    def add_candle(self, candle):
        self.std_indicator.add_candle(candle)
        self.is_subplot = True
        data_size = len(self.candles_dict.values())
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            period_std = self.std_indicator.data.iloc[-1]['y']
            z_score = (candle.close - self.std_indicator.period_avg) / period_std
            self.data_dict['y'].append(z_score)
            self.data_dict['candles'].append(candle)
        self.data = DataFrame(data=self.data_dict)


class RelativeStrengthIndex(BaseIndicator):

    def __init__(self, **options):
        super().__init__(**options)
        self.indicator_id = 'relative_strength_index'

    def add_candle(self, candle):
        self.is_subplot = True
        data_size = len(self.candles_dict.values())
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            period_avg_gain = sum(
                    [getattr(list(self.candles_dict.values())[j], self.options['on']) - getattr(list(self.candles_dict.values())[j-1], self.options['on']) for j in range(
                        data_size - self.period, data_size
                    ) if getattr(list(self.candles_dict.values())[j], self.options['on']) - getattr(list(self.candles_dict.values())[j-1], self.options['on']) > 0]
                ) / self.period
            period_avg_loss = sum(
                    [getattr(list(self.candles_dict.values())[j], self.options['on']) - getattr(list(self.candles_dict.values())[j-1], self.options['on']) for j in range(
                        data_size - self.period, data_size
                    ) if getattr(list(self.candles_dict.values())[j], self.options['on']) - getattr(list(self.candles_dict.values())[j-1], self.options['on']) < 0]
                ) / self.period
            period_rs = period_avg_gain / period_avg_loss
            period_rsi = 100 - (100 / (1 + period_rs))
            self.data_dict['y'].append(period_rsi)
            self.data_dict['candles'].append(candle)
        self.data = DataFrame(data=self.data_dict)


class DifferenceBetween(BaseIndicator):

    def __init__(self, indicators: list[BaseIndicator], **options):
        super().__init__(**options)
        self.indicators = indicators
        self.indicator_id = 'difference_between'
        self.period = max([indicator.period for indicator in indicators])

    def add_candle(self, candle):
        self.is_subplot = True
        data_size = len(self.candles_dict.values())
        for indicator in self.indicators:
            indicator.add_candle(candle)
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            indicator_1 = self.indicators[0].data.iloc[-1]['y']
            indicator_2 = self.indicators[1].data.iloc[-1]['y']
            diff = indicator_1 - indicator_2
            self.data_dict['y'].append(diff)
            self.data_dict['candles'].append(candle)

        self.data = DataFrame(data=self.data_dict)

# My own


class AverageDifference(BaseIndicator):

    def __init__(self, **options):
        super().__init__(**options)
        self.indicator_id = 'average_difference'

    def add_candle(self, candle):
        self.is_subplot = True
        data_size = len(self.candles_dict.values())
        if data_size < self.period and candle.time not in self.candles_dict:
            self.data_dict['x'].append(None)
            self.data_dict['y'].append(None)
            self.data_dict['candles'].append(None)
            self.candles_dict[candle.time] = candle
        elif data_size >= self.period:
            self.candles_dict[candle.time] = candle
            self.data_dict['x'].append(candle.time)
            cand_vals = list(self.candles_dict.values())
            period_diff_sum = sum(
                    [getattr(candle, self.options['on']) - getattr(cand_vals[j], self.options['on']) for j in range(
                        data_size - self.period, data_size
                    )]
                )
            period_avg_diff = period_diff_sum / self.period
            self.data_dict['y'].append(period_avg_diff)
            self.data_dict['candles'].append(candle)
        self.data = DataFrame(data=self.data_dict)