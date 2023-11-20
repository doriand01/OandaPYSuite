from oandapysuite.settings import AUTH_FILEPATH
from oandapysuite.endpoints import account
from oandapysuite.endpoints import instrument
from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite.objects.datatypes import UnixTime

from requests import get

import plotly.graph_objects as plot

from pandas import DataFrame





class API:
    """Object that allows the user to access OANDA's REST API endpoints. In order to
    initialize this class, the constructor must be passed a file URI containing the
    user's API auth token. For example, if you have it located in your documents folder,
    it would be `x = APIObject('~/Documents/auth.txt')`"""

    def get_candles(self, ins, gran, count=None, _from=None, to=None):
        """Returns a CandleCluster object containing candles with historical data. `ins` should be
        a string containing the currency pair you would like to retreive, in the form of BASE_QUOTE.
        (eg. USD_CAD). `gran` is the granularity of the candles, and should be a string specifying
        any granularity that you would find in a typical market chart (eg. 'M1', 'M5', 'H1') etc...
        `count` is an optional variable that returns the specified number of candles. Should be an int.
        `_from` and `to` are for if you would prefer to retreive candles from a certain time range.
        These values should be an integer in the format of the UNIX epoch (seconds elapsed since 
        1 January 1970.)"""

        # There are two ways to determine the desired range for the retrieval of candle data. The first is by
        # count. Count will retrieve x number of candles from the past preceding the latest available candle from
        # the market. The default for the API.get_candles() function is 500. The second way to determine candlestick
        # range is by time. Two unix times can be specified (a from value and a two value) and all candlesticks that fall
        # between the two times (Unix Epoch timestamp) will be retrieved.
        if count:
            response = get(instrument.Instrument.get_candles(ins,gran, count=count),headers=self.auth_header)
        else:
            response = get(instrument.Instrument.get_candles(ins,gran, from_time=UnixTime(_from), to_time=UnixTime(to)), headers=self.auth_header)
        return CandleCluster(response.text)
        
    def get_child_candles(self, candle, gran):
        """Returns the children candles (in the form of a CandleCluster object) of a specified 
        candle at the specified granuarlity. For example, passing in an H1 candle from 00:00-01:00 
        on 1 January, using 'M1' as the desired child granularity, will yield a CandleCluster object 
        containing 60 M1 candles, ranging from the start of the parent candle to the end of the parent candle."""

        start = int(candle.time.timestamp()) - candlex[candle.gran]
        end = int(candle.time.timestamp())
        return self.get_instrument_candles(candle.instrument, gran, _from=start, to=end)

    def initialize_chart(self, candle_data: CandleCluster):
        cluster_df = candle_data.to_dataframe()
        self.fig =  plot.Figure(
            data=[
                    plot.Candlestick(
                        x=cluster_df['time'],
                        open=cluster_df['open'],
                        high=cluster_df['high'],
                        low=cluster_df['low'],
                        close=cluster_df['close'],


                    )],
            layout={'yaxis': {'fixedrange': False},
                    'title': {'text': f'{candle_data.instrument} {candle_data.gran}'}
            }
        )

    def add_indicator(self, indicator: BaseIndicator):
        self.fig.add_trace(
            plot.Scatter(
                name=indicator.name,
                x = indicator.data['x'],
                y = indicator.data['y'],
            mode='lines',
            line=plot.scatter.Line(color=indicator.color)),
        )
    def render_chart(self):
        self.fig.show()


            

    def __init__(self):
        self.auth = str(open(AUTH_FILEPATH, 'r').read())
        self.auth_header = {
            'Authorization': f'Bearer {self.auth}'
        }

                
        
        
        

