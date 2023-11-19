
DEMO_API_ENDPOINT = 'https://api-fxpractice.oanda.com'
LIVE_API_ENDPOINT = 'https://api-fxtrade.oanda.com'

API_VERSION = 'v3'

AUTH_FILEPATH = "C:\\Users\\preit\\OneDrive\\Desktop\\OandaAPIkey.txt"
DEMO_MODE = True
REQUEST_PREFIX = f'{DEMO_API_ENDPOINT if DEMO_MODE == True else LIVE_API_ENDPOINT}/{API_VERSION}'

DATETIME_REGEX = '(?P<hhmmss>\d{2}:\d{2}(?::\d{2})*)|(\d{4}[ -]\d{1,2}[ -]\d{1,2}(\s{1}(?P=hhmmss))?)'