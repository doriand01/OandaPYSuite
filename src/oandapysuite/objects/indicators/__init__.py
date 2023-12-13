from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.exceptions import IndicatorOptionsError

import math
import decimal

import numpy as np
from pandas import DataFrame, Series
from ta import volatility



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

    def update(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        """
        Provide your own implementation of this function to calculate your indicator.
        self.data must be set to the new data with the following shape:
        A pandas dataframe with two columns (x, y) and the same number of rows as the number of candles in the
        candle_cluster object. The x column must contain the time of each candle, and the y column must contain
        the value of your indicator for each candle.
        """
        self.data = DataFrame(data={})

    def _validate_options(self, options: dict):
        a = [required_option in options.keys() for required_option in self.required_options]
        pass
        if not all([required_option in options.keys() for required_option in self.required_options]):
            raise IndicatorOptionsError(f'{self.__class__.__name__}, requires the options {self.required_options}')

    def __init__(self, **options):
        """
        __init__(
            self,
            options: dict(), <--- Parameters for your indicator. eg. period, etc...
            )
        """
        self._validate_options(options)
        for key, value in options.items():
            setattr(self, key, value)
        self.is_subplot = False
        self.y_count = 1
        self.options = options
        self.data = DataFrame(
                data={
                    'candles' : [],
                    'x'       : [],
                    'y'       : []
                }
            )
from oandapysuite.objects.indicators import trend, volatility, volume, momentum, other