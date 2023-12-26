from oandapysuite import exceptions
from oandapysuite.settings import AUTH_FILEPATH
from oandapysuite.endpoints import account as acc
from oandapysuite.endpoints import instrument
from oandapysuite.objects import trade
from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite.objects.indicators.volatility import AverageDifference
from oandapysuite.objects.datatypes import UnixTime, candlex

import json
import logging
from time import sleep
from datetime import datetime, timedelta
from copy import deepcopy
from requests import get, post, put


import plotly.graph_objects as plot
from plotly.subplots import make_subplots as subplot
from pandas import DataFrame

logging.basicConfig(filename='sigs.log', encoding='utf-8', level=logging.WARN)


class API:
    """Object that allows the user to access OANDA's REST API endpoints. In order to
    initialize this class, the auth token filepath URI must first be configured in the settings."""

    @staticmethod
    def __calculate_view_height(num_subplots):
        if num_subplots == 0:
            return [1]
        return [0.8] + [(1-0.8)/num_subplots] * num_subplots

    def get_candles(self, ins, gran, count=None, start=None, end=None):
        """
        Returns candle clusters from a specified period.

        get_candles(
            self,
            ins: str <-- Must be a valid forex instrument (currency pair.)
            gran: str <-- Candlestick granularity. Ranges from H1 to S5
            count=None Must be specified of _from and to are not set.
            _from: UnixTime <-- Time in form of a UnixTime object
            to: UnixTime <-- Time in form of a UnixTime object
        )
        """

        # There are two ways to determine the desired range for the retrieval of candle data. The first is by
        # count. Count will retrieve x number of candles from the past preceding the latest available candle from
        # the market. The default for the API.get_candles() function is 500. The second way to determine candlestick
        # range is by time. Two unix times can be specified (a from value and a two value) and all candlesticks that
        # fall between the two times (Unix Epoch timestamp) will be retrieved.
        if count:
            response = get(instrument.Instrument.get_candles(ins,gran, count=count),headers=self.auth_header)
        else:
            if type(start) == int and type(end) == int:
                start_dt_obj = datetime.now() - timedelta(seconds=start*candlex[gran])
                end_dt_obj = datetime.now() - timedelta(seconds=end*candlex[gran])
                start_unix_obj = UnixTime(start_dt_obj.strftime('%Y-%m-%d %H:%M'))
                end_unix_obj = UnixTime(end_dt_obj.strftime('%Y-%m-%d %H:%M'))
                response = get(instrument.Instrument.get_candles(ins, gran, from_time=start_unix_obj, to_time=end_unix_obj), headers=self.auth_header)
            elif type(start) == UnixTime and type(end) == UnixTime:
                response = get(instrument.Instrument.get_candles(ins, gran, from_time=start, to_time=end), headers=self.auth_header)

        if response.status_code != 200:
            raise exceptions.APIError(response.status_code,response.text)
        return CandleCluster(response.text)

    def load_accounts(self):
        """
        Loads tradeable accounts available for the authorized token. `load_account()` must be called before calling any
         methods that involve accesing trading endpoints, like `open_trade()` or `close_trade()`. After loading your
         accounts, call `select_account()` to choose an account to trade with.

        load_accounts(self)
        """
        accounts = json.loads(get(acc.Account.get_accounts_for_token, headers=self.auth_header).text)['accounts']
        for account in accounts:
            account_obj = trade.Account(account)
            self.available_accounts.append(account_obj)

    def select_account(self, index=0):
        """
        Selects loaded tradeable account. Must be called after `load_account()` and before calling any methods that
        access trading endpoints like `open_trade()` or `close_trade()`.

        select_account(
            self,
            index: int = 0
        )

        * The stored and previously loaded accounts are stored as an object attribute `self.loaded_accounts`
        * If you want to select the loaded account at index 0 in this list, call `select_account(0)`.
        * index is 0 by default.
        """

        if not self.available_accounts:
            raise exceptions.AccountsNotLoadedError
        else:
            self.selected_account = self.available_accounts[index]

    def open_trade(self, instrument, units):
        """
        Opens a trade on the market.

        open_trade(
            self,
            instrument: str
            units: int
        )
        * Units should be an integer.
        * To enter a long, units should be positive. To enter a short, they should be negative.
        """

        # Raises a NoAccountSelectedError if select_account() hasn't been called before opening a trade.
        if not self.selected_account:
            raise exceptions.NoAccountSelectedError()
        else:
            # The API object has a list of currently open trades stored as a list of strings containing the trade's
            # Transaction ID.
            req_url, order_body = acc.Account.create_order(instrument, units, self.selected_account.id)
            response = post(req_url, headers=self.auth_header,json=order_body)
            self.open_trades.append(json.loads(response.text)['lastTransactionID'])

    def close_trade(self, trans_id, units="ALL"):
        """
        Closes a trade on the market. The transaction id of the trade must be provided.

        close_trade(
            self,
            trans_id: str
            units: str or int
        )

        * If units is are specified, a partial close will be executed.
        * If no units are specified, the whole position will be closed.
        """
        if not self.selected_account:
            raise exceptions.NoAccountSelectedError("No account selected. Select an account with `select_account()`")
        else:
            req_url, order_body = acc.Account.close_trade(self.selected_account.id, trans_id, units)
            response = put(req_url, headers=self.auth_header)
            self.open_trades.remove(trans_id)

    def trade_signal(self, instrument,  signal, candle):
        cur_price = candle.close
        if signal == 1 and not self.open_trades:
            print(f'Signal 1 detected, entering trade long @ {cur_price} on {instrument}')
            self.open_trade(instrument, 50000)
        if signal == 2 and not self.open_trades:
            print(f'Signal 2 detected, entering trade short @ {cur_price} on {instrument}')
            self.open_trade(instrument, -50000)
        if signal == 3 and len(self.open_trades) > 0:
            print(f'Signal 3 detected, exiting long @ {cur_price} on {instrument}')
            self.close_trade(self.open_trades[0])
        if signal == 4 and len(self.open_trades) > 0:
            print(f'Signal 4 detected, exiting short @ {cur_price} on {instrument}')
            self.close_trade(self.open_trades[0])
    def get_order_book(self, instrument):
        response = get(instrument.Instrument.get_order_book(instrument))

    def get_child_candles(self, candle: CandleCluster.Candle, gran: str) -> CandleCluster:
        """Returns the children candles (in the form of a CandleCluster object) of a specified 
        candle at the specified granularity. For example, passing in an H1 candle from 00:00-01:00
        on 1 January, using 'M1' as the desired child granularity, will yield a CandleCluster object 
        containing 60 M1 candles, ranging from the start of the parent candle to the end of the parent candle."""

        start = int(candle.time.timestamp())
        end = int(candle.time.timestamp()) + candlex[candle.gran]
        return self.get_candles(candle.instrument, gran, start=UnixTime(start), end=UnixTime(end))

    def initialize_chart(self, candle_data: CandleCluster, type='candlestick'):
        cluster_df = candle_data.to_dataframe()
        if type == 'candlestick':
            data_trace = plot.Candlestick(
                            x=cluster_df['time'],
                            open=cluster_df['open'],
                            high=cluster_df['high'],
                            low=cluster_df['low'],
                            close=cluster_df['close'])
        elif type == 'ohlc':
            data_trace = plot.Ohlc(
                            x=cluster_df['time'],
                            open=cluster_df['open'],
                            high=cluster_df['high'],
                            low=cluster_df['low'],
                            close=cluster_df['close'])
        self.fig = plot.Figure(
            data=[data_trace],
            layout={'yaxis': {'fixedrange': False},
                    'title': {'text': f'{candle_data.instrument} {candle_data.gran}'}
            }
        )

    def add_indicator(self, indicator: BaseIndicator):
        if indicator.is_subplot:
            old_fig = deepcopy(self.fig)
            self.fig = subplot(rows=len(old_fig.data)+1, cols=1, row_heights=API.__calculate_view_height(len(old_fig.data)), shared_xaxes=True)
            for i in range(len(old_fig.data)):
                self.fig.add_trace(old_fig.data[i], row=i+1, col=1)
            self.fig.add_trace(plot.Scatter(
                name=indicator.name,
                x=indicator.data['x'],
                y=indicator.data['y'],
                mode='lines',
                line=plot.scatter.Line(color=indicator.color)),
                row=len(old_fig.data)+1,
                col=1)
        else:
            if indicator.y_count > 1:
                for i in range(indicator.y_count):
                    self.fig.add_trace(
                        plot.Scatter(
                            name=indicator.name,
                            x = indicator.data['x'],
                            y = indicator.data[f'y{i+1}'],
                            mode='lines',
                            line=plot.scatter.Line(color=indicator.color)),
                    )
            elif indicator.y_count == 1:
                self.fig.add_trace(
                    plot.Scatter(
                        name=indicator.name,
                        x = indicator.data['x'],
                        y = indicator.data['y'],
                        mode='lines',
                        line=plot.scatter.Line(color=indicator.color)),
                )

    def render_chart(self, live=False, data_df=None):
        self.fig.update_layout(xaxis_rangeslider_visible=False)
        self.fig.show()

    def __init__(self):
        self.auth = str(open(AUTH_FILEPATH, 'r').read())
        self.auth_header = {
            'Authorization': f'Bearer {self.auth}'
        }
        self.available_accounts = []
        self.selected_account = None
        self.open_trades = []