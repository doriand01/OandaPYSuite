
DEMO_API_ENDPOINT = 'https://api-fxpractice.oanda.com'
LIVE_API_ENDPOINT = 'https://api-fxtrade.oanda.com'

# Should be either v3 or v20
API_VERSION = 'v3'

# Path to your auth file. Should be a plain text file containing nothing but the account's API
# auth token.
AUTH_FILEPATH = "C:\\Users\\preit\\OneDrive\\Desktop\\OandaAPIkey.txt"

# Demo mode determines whether the requests will be made to OANDA's demo API endpoint (fake practice money)
# Or OANDA's live trading endpoint (real not practice money)
DEMO_MODE = True
REQUEST_PREFIX = f'{DEMO_API_ENDPOINT if DEMO_MODE == True else LIVE_API_ENDPOINT}/{API_VERSION}'

# Used to parse out dates and times when instantiating the UnixTime object.
DATETIME_REGEX = '(?P<hhmmss>\d{2}:\d{2}(?::\d{2})*)|(\d{4}[ -]\d{1,2}[ -]\d{1,2}(\s{1}(?P=hhmmss))?)'

INDICATOR_ALIASES = {
    'ExponentialMovingAverage' : 'oandapysuite.objects.indicators.trend.ExponentialMovingAverage',
    'SimpleMovingAverage'      : 'oandapysuite.objects.indicators.trend.SimpleMovingAverage',
    'TRIX'                     : 'oandapysuite.objects.indicators.trend.TRIX',
    'AverageDirectionalMovementIndex' : 'oandapysuite.objects.indicators.trend.AverageDirectionalMovementIndex',
    'ParabolicSAR'             : 'oandapysuite.objects.indicators.trend.ParabolicSAR',
    'DetrendedPriceOscillator' : 'oandapysuite.objects.indicators.trend.DetrendedPriceOscillator',
    'MACD'                     : 'oandapysuite.objects.indicators.trend.MovingAverageConvergenceDivergence',
    'AwesomeOscillator'        : 'oandapysuite.objects.indicators.momentum.AwesomeOscillator',
    'PercentagePriceOscillator': 'oandapysuite.objects.indicators.momentum.PercentagePriceOscillator',
    'RateOfChange'             : 'oandapysuite.objects.indicators.momentum.RateOfChange',
    'RelativeStrengthIndex'    : 'oandapysuite.objects.indicators.momentum.RelativeStrengthIndex',
    'StochasticOscillator'     : 'oandapysuite.objects.indicators.momentum.StochasticOscillator',
    'TrueStrengthIndex'        : 'oandapysuite.objects.indicators.momentum.TrueStrengthIndex',
    'KAMA'                     : 'oandapysuite.objects.indicators.momentum.KAMA',
    'StochasticRSI'            : 'oandapysuite.objects.indicators.momentum.StochasticRSI',
    'UltimateOscillator'       : 'oandapysuite.objects.indicators.momentum.UltimateOscillator',
    'WilliamsR'                : 'oandapysuite.objects.indicators.momentum.WilliamsR',
    'SampleStandardDeviation'  : 'oandapysuite.objects.indicators.volatility.SampleStandardDeviation',
    'BollingerBands'           : 'oandapysuite.objects.indicators.volatility.BollingerBands',
    'KeltnerChannels'          : 'oandapysuite.objects.indicators.volatility.KeltnerChannels',
    'UlcerIndex'              : 'oandapysuite.objects.indicators.volatility.UlcerIndex',
    'AverageTrueRange'         : 'oandapysuite.objects.indicators.volatility.AverageTrueRange',
    'DonchianChannels'         : 'oandapysuite.objects.indicators.volatility.DonchianChannels',




}