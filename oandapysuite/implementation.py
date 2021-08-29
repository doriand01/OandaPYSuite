

import json
import decimal
import os
import time

from requests import get, put, post
from datetime import datetime
from re import sub
from string import printable
from matplotlib import pyplot
from numpy import array

from oandapysuite.endpoints import *
from oandapysuite.stats import *
from oandapysuite.exceptions import *

time_format = '%Y-%m-%dT%X'
decimal.getcontext().prec = 6
D = decimal.Decimal

"""This class serializes JSON data received when using
OANDAAPIObject to retreive candledata. It can be iterated
over like a list, and each individual candle is its own
object. The CandlesObject class is essentially a list of
individual candle objects."""
class CandlesObject:

    class Candle:
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
                if self.candles[i].close > self.candles[i-1].close:
                    self.candles[i].is_bull = True
                    self.candles[i].is_bear = False
                else:
                    self.candles[i].is_bull = False
                    self.candles[i].is_bear = True
                if self.candles[i].is_bull == self.candles[i-1].is_bull:
                    self.candles[i].reversal = False
                else:
                    self.candles[i].reversal = True
            self.std = standard_deviation([i.close for i in self.candles[-30:]])
    
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

    def history(self, valuex=None, valuey=None):
        historic_data = {'x' : [],
                         'y' : []}
        if valuex and valuey:
            for candle in self.candles:
                historic_data['x'].append(getattr(candle, valuex))
                historic_data['y'].append(getattr(candle, valuey))
            return (historic_data['x'], historic_data['y'])
        if not valuey:
            return [getattr(candle, valuex) for candle in self.candles]


class OANDAAPIObject:

    def get_instrument_candles(self, ins, gran, count=500, _from=None, to=None):
        headers = {
            'Authorization': f'Bearer {self.auth}'
        }
        response = get(get_candle(ins, gran, count=count, _from=_from, to=to), headers=headers)
        return CandlesObject(response.text)

    def get_child_candles(self, candle, gran):
        start = int(candle.time.timestamp()) - candlex[candle.gran]
        end = int(candle.time.timestamp())
        return self.get_instrument_candles(candle.instrument, gran, _from=start, to=end)

            

    def __init__(self, auth):
        self.auth = str(open(auth, 'r').read())
    
    @staticmethod
    def plot(x=None, y=None, style='scatter'):
        x = array(x)
        y = array(y)
        getattr(pyplot, style)(x, y)

    @staticmethod
    def visualize():
        pyplot.show()

                
        
        
        

