from oandapysuite import settings
from oandapysuite import exceptions
from oandapysuite import api
from oandapysuite import stats
from oandapysuite import endpoints
from oandapysuite import objects

SMA = objects.indicators.SimpleMovingAverage
SSTD = objects.indicators.SampleStandardDeviation

if not settings.AUTH_FILEPATH:
    print("""No file containing the API Authorization token has been specified. \n
            If you have your API key with you, place it in a .txt file and type paste \n
            the full filepath below. Else, run oandapysuite.config(), later to set up your \n
            configuration.\n""")
    auth_file = input("Path to API key:")
    settings.AUTH_FILEPATH = auth_file