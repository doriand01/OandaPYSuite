from oandapysuite.settings import *


class Account:
    """Account class. This class contains functions that render URL endpoints to make requests to the REST API."""

    get_accounts_for_token = f'{REQUEST_PREFIX}/accounts'
    get_account_details = lambda accid: f'{REQUEST_PREFIX}/accounts/{accid}'
    get_account_summary = lambda accid: f'{REQUEST_PREFIX}/accounts/{accid}/summary'

    @staticmethod
    def close_trade(account_id, specifier, units):
        order_body = {
            'units' : units
        }

        return f'{REQUEST_PREFIX}/accounts/{account_id}/trades/{specifier}/close',  order_body

    @staticmethod
    def get_trades(account_id, specifier=None):
        if not specifier:
            return f'{REQUEST_PREFIX}/accounts/{account_id}/trades'
        else:
            return f'{REQUEST_PREFIX}/accounts/{account_id}/trades'
    @staticmethod
    def create_order(instrument, units, account_id):
        order_body = {
          "order": {
            "units": units,
            "instrument": instrument,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
          }
        }
        return f'{REQUEST_PREFIX}/accounts/{account_id}/orders', order_body