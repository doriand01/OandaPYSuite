from oandapysuite.exceptions import HighestGranularityException, LowestGranularityException
from oandapysuite.objects.datatypes import candlex

import json
import numpy as np

from datetime import datetime, timedelta
from pytz.reference import LocalTimezone
from time import timezone
from copy import deepcopy

from pandas import DataFrame, Series, concat



time_format = '%Y-%m-%dT%X'


class CandleCluster:
    """This class serializes JSON data received when using the API class to retreive data from the market. It can be
    iterated over like a list, and each individual candle is its own object. The CandleCluster class is essentially a
    list of individual candle objects. This class should never be directly accessed by the user for instantiation. If
    the user wishes to create a CandleCluster object or retrieve candles, they should use the `get_candles()` method of
    the API."""

    def __init__(self, candsjson=None, cand_list=None):
        if candsjson:
            self.candledata = json.loads(candsjson)
            self.gran = self.candledata['granularity']
            self.instrument = self.candledata['instrument'].replace('/', '_')
            self.candles = np.array(
                [(float(c['mid']['o']),
                  float(c['mid']['h']),
                  float(c['mid']['l']),
                  float(c['mid']['c']),
                  datetime.strptime(c['time'][:-11], time_format))
                 for c in self.candledata['candles']],
            )

    def __str__(self):
        return f'<{len(self.candles)} candles, time: {self.candles[0][4]} thru {self.candles[-1][4]}>'

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.candles)

    def __next__(self):
        return next(self.candles)

    def __getitem__(self, index):
        return self.candles[index]

    def __len__(self):
        return len(self.candles)

    def __add__(self, b):
        if not self.instrument == b.instrument:
            raise ClusterConcatException(self.instrument, b.instrument)

        # Checks to see if the open time on the first candle in self is greater than the open time on the last candle in
        # the cluster which is being added to self. If it is, the b is copied into the resultant CandleCluster using
        # `deepcopy`, and the self is appended to it. The resultant CandleCluster is then returned.
        if self[0].time > b[-1].time:
            self.candles = np.concatenate(b.candles, self.candles)
            return result

        # If the first open of the first candle in b is greater than the open of the first candle in self, then the
        # inverse operation is done and the resultant object is b appended to self.
        elif b[0].time > self[-1].time:
            self.candles = np.concatenate([self.candles, b.candles])
            return self

    def history(self, prop):
        """
        Returns specified historic data from every `Candle` in a `CandleCluster`object in the form of a list.
        May potentially be deprecated by `to_dataframe()` method in the future.

        history(
            *options: str
        )

        * Retrieve attributes from every candle by specifying the option. For example, if you want the open from
        every candle in the candle cluster, you would pass 'open' as a string into the arguments.
        """
        if prop == 'open':
            return self.candles[:, 0]
        elif prop == 'high':
            return self.candles[:, 1]
        elif prop == 'low':
            return self.candles[:, 2]
        elif prop == 'close':
            return self.candles[:, 3]
        elif prop == 'time':
            return self.candles[:, 4]

    def to_dataframe(self):
        """
        Returns the CandleCluster object as an OHLC+Time dataframe. Takes no arguments.

        to_dataframe(self)

        """
        data_dict = {
            'open' : self.history('open'),
            'high' : self.history('high'),
            'low'  : self.history('low'),
            'close':self.history('close'),
            'time' : self.history('time')
        }
        return DataFrame(data=data_dict)


