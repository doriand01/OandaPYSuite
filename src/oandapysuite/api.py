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
import numpy as np

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


        # The OANDA API can only retrieve 5000 candles per request. Therefore, when count is specified as a parameter,
        # it must be checked to see if it is greater than 5000. If it is, the function will make multiple requests to
        # the API to retrieve all the candles in the specified range. These requests are broken up into chunks of 5000
        # candles each, and the function will return a CandleCluster object containing all the candles in the specified
        # range. It must be noted that providing a value of 5,000 candles will only return all candles for the most
        # recent X periods specified. This means that if the specified time range falls within a period where the market
        # is closed (ie. there are no candles for that period), the function will return less than the requested amount
        # of candles.
        if count and count < 5000:
            response = get(instrument.Instrument.get_candles(ins,gran, count=count),headers=self.auth_header)
            if response.status_code != 200:
                raise exceptions.APIError(response.status_code,response.text)


        elif count > 5000:
            # Create a dictionary that stores the start and end timestamps of each of the chunks.
            chunks_datetimes = {}
            chunks = count // 5000

            # Calculate the remainder of the count divided by 5000 to determine how many periods are left over after
            # the chunks are retrieved.
            remainder = count % 5000

            # Retrieve the first 5000 candles.
            first_5000_response = get(instrument.Instrument.get_candles(ins, gran, count=5000), headers=self.auth_header)

            # The final candle cluster object is instantiated with the first 5,000 candles.
            final_candles = CandleCluster(first_5000_response.text)

            # This for loop iterates over the chunk dictionary, retrieving candles for the specified period for each
            # chunk. The candles are then concatenated to the final_candles object.
            for i in range(chunks):

                # Skip the first iteration, as the first 5000 candles have already been retrieved.
                if i == 0:
                    continue
                else:
                    # Calculate the start and end timestamps for each chunk.
                    if i == 1:
                        chunk_end = int(final_candles[0][4].timestamp())
                    elif i > 1:
                        chunk_end = chunks_datetimes[i-1][0]
                    chunk_start = int(chunk_end - 5000 * candlex[gran])
                    chunks_datetimes[i] = (chunk_start, chunk_end)

            for chunk in chunks_datetimes.values():
                # Create each chunk of candles and concatenate them to the final_candles object.
                response = get(instrument.Instrument.get_candles(ins, gran, from_time=UnixTime(chunk[0]), to_time=UnixTime(chunk[1])), headers=self.auth_header)
                chunk_candles = CandleCluster(response.text)
                final_candles = np.concatenate([chunk_candles, final_candles])

            # After the chunks have all been retrieved, the remainder candles are retrieved and concatenated to the
            # final_candles object.
            remainder_chunk_start = int(final_candles[0][4].timestamp() - (remainder * candlex[gran]))
            remainder_chunk_end = int(final_candles[0][4].timestamp())
            response = get(instrument.Instrument.get_candles(ins, gran, from_time=UnixTime(remainder_chunk_start), to_time=UnixTime(remainder_chunk_end)), headers=self.auth_header)
            remainder_candles = CandleCluster(response.text)
            if len(remainder_candles) == 0:
                return final_candles
            else:
                final_candles = np.concatenate([remainder_candles, final_candles])
                return final_candles




        else:
            if type(start) == int and type(end) == int:
                start_dt_obj = datetime.now() - timedelta(seconds=start*candlex[gran])
                end_dt_obj = datetime.now() - timedelta(seconds=end*candlex[gran])
                start_unix_obj = UnixTime(start_dt_obj.strftime('%Y-%m-%d %H:%M'))
                end_unix_obj = UnixTime(end_dt_obj.strftime('%Y-%m-%d %H:%M'))
                response = get(instrument.Instrument.get_candles(ins, gran, from_time=start_unix_obj, to_time=end_unix_obj), headers=self.auth_header)
            elif type(start) == UnixTime and type(end) == UnixTime:
                response = get(instrument.Instrument.get_candles(ins, gran, from_time=start, to_time=end), headers=self.auth_header)

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

    def __init__(self):
        self.auth = str(open(AUTH_FILEPATH, 'r').read())
        self.auth_header = {
            'Authorization': f'Bearer {self.auth}'
        }
        self.available_accounts = []
        self.selected_account = None
        self.open_trades = []