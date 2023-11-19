from oandapysuite.settings import *


class Account:
    """Account class. This class contains lambda functions that render
    URL endpoints to make requests to the REST API."""

    get_accounts_for_token = f'{REQUEST_PREFIX}/v3/accounts'
    get_summary = lambda accid: f'{accounts_for_token}/{accid}'