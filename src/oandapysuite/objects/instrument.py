from oandapysuite.stats import candlex
from oandapysuite.exceptions import HighestGranularityException, LowestGranularityException

import json
import decimal
from datetime import datetime
from time import timezone

from pandas import DataFrame

D = decimal.Decimal
decimal.getcontext().prec = 6
time_format = '%Y-%m-%dT%X'


class CandleCluster:
    """This class serializes JSON data received when using OANDAAPIObject to retreive candledata. It can be iterated
    over like a list, and each individual candle is its own object. The CandlesObject class is essentially a list of
    individual candle objects. This class should never be directly accessed by the user for instantiation. If the
    user wishes to create a CandleCluster object or retrieve candles, they should use the `get_candles()` method of the
    API."""
    class Candle:
        """Serializes candle data."""

        def __init__(self, candledata, ins, gran):
            global time_format
            self.open = D(candledata['mid']['o'])
            self.close = D(candledata['mid']['c'])
            self.low = D(candledata['mid']['l'])
            self.high = D(candledata['mid']['h'])
            self.oc_displacement = self.close - self.open
            self.total_displacement = self.high - self.low
            self.complete = True if candledata['complete'] == 'true' else False
            # Subtracts offset of current timezone from UTC time returned by OANDA API to get local time.
            self.time = datetime.fromtimestamp(datetime.strptime(candledata['time'][:-11], time_format).timestamp() - timezone)
            self.volume = int(candledata['volume'])
            self.gran = gran
            self.instrument = ins

        def get_lower_timeframe(self) -> str:
            granularities = list(candlex.keys())
            gran_index = granularities.index(self.gran)
            if gran_index == 0:
                raise LowestGranularityException
            return granularities[gran_index-1]

        def get_higher_timeframe(self) -> str:
            granularities = list(candlex.keys())
            gran_index = granularities.index(self.gran)
            if gran_index == len(granularities)-1:
                raise HighestGranularityException
            return granularities[gran_index+1]

        def has_lower_timeframe(self) -> bool:
            granularities = list(candlex.keys())
            return granularities.index(self.gran) != 0

        def __str__(self):
            return f'<{self.time}, close: {self.close}, timeframe: {self.gran}>'

        def __repr__(self):
            return self.__str__()

    def __init__(self, candsjson=None, cand_list=None):
        self.candles = []
        self.ind = 0
        if candsjson:
            self.candledata = json.loads(candsjson)
            self.gran = self.candledata['granularity']
            self.instrument = self.candledata['instrument'].replace('/', '_')
            for candle in self.candledata['candles']:
                self.candles.append(self.Candle(candle, self.instrument, self.gran))

        else: self.candles = cand_list

    def has_lower_timeframe(self) -> bool:
        return self.candles[0].has_lower_timeframe()

    def __str__(self):
        return f'<{len(self.candles)} candles, time: {self.candles[0].time} thru {self.candles[-1].time}>'

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.candles)

    def __next__(self):
        ind = self.ind
        self.ind += 1
        return ind

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
            result = deepcopy(b)
            for candle in self:
                result.candles.append(candle)

        # If the first open of the first candle in b is greater than the open of the first candle in self, then the
        # inverse operation is done and the resultant object is b appended to self.
        elif b[0].time > self[-1].time:
            result = deepcopy(self)
            for candle in b:
                result.candles.append(candle)
        return result

    def history(self, *properties) -> list:
        """
        Returns specified historic data from every `Candle` in a `CandleCluster`object in the form of a list.
        May potentially be deprecated by `to_dataframe()` method in the future.

        history(
            *options: str
        )

        * Retrieve attributes from every candle by specifying the option. For example, if you want the open from
        every candle in the candle cluster, you would pass 'open' as a string into the arguments.
        """
        data = []
        for prop in properties:
            data.append([getattr(candle, prop) for candle in self.candles])
        return data

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


