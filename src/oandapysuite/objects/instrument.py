import json
import decimal
from pandas import DataFrame

from datetime import datetime

D = decimal.Decimal
decimal.getcontext().prec = 6
time_format = '%Y-%m-%dT%X'
class CandleCluster:
    """This class serializes JSON data received when using
    OANDAAPIObject to retreive candledata. It can be iterated
    over like a list, and each individual candle is its own
    object. The CandlesObject class is essentially a list of
    individual candle objects."""
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
            self.time = datetime.strptime(candledata['time'][:-11], time_format)
            self.volume = int(candledata['volume'])
            self.gran = gran
            self.instrument = ins
            self.reversal = None
            self.is_bull = None
            self.is_bear = None

        def __str__(self):
            return f'<{self.time}, close: {self.close}>'

        def __repr__(self):
            return self.__str__()


    def __init__(self, candsjson):
        self.candledata = json.loads(candsjson)
        self.candles = []
        self.ind = 0
        self.gran = self.candledata['granularity']
        self.instrument = self.candledata['instrument'].replace('/', '_')
        for candle in self.candledata['candles']:
            self.candles.append(self.Candle(candle, self.instrument, self.gran))
        for i in range(len(self.candles)):
            if i == 0: continue
            if self.candles[i].close > self.candles[ i -1].close:
                self.candles[i].is_bull = True
                self.candles[i].is_bear = False
            else:
                self.candles[i].is_bull = False
                self.candles[i].is_bear = True
            if self.candles[i].is_bull == self.candles[ i -1].is_bull:
                self.candles[i].reversal = False
            else:
                self.candles[i].reversal = True

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
        if self[0].time > b[-1].time:
            result = deepcopy(b)
            for candle in self:
                result.candles.append(candle)
        elif b[0].time > self[-1].time:
            result = deepcopy(self)
            for candle in b:
                result.candles.append(candle)
        return  result


    def history(self, valuex=None, valuey=None):
        """Returns historic data from every `Candle` in a `CandleCluster`
        object in the form of a list. For example, in order to get the close
        on every candle in a CandleCluster object `x`, you would use
        `x.history('close')`. You can also retreive historic data in the form
        of a two dimensional tuple, by passing in your specified values for `valuex`
        and `valuey`. All values passed in must be attributes of the `Candle` object."""
        return [getattr(candle, valuex) for candle in self.candles]

    def to_dataframe(self):
        data_dict = {
                    'open' : self.history('open'),
            'high' : self.history('high'),
            'low' : self.history('low'),
            'close' :self.history('close'),
            'time' : self.history('time')
        }
        return DataFrame(data=data_dict)


