import oandapysuite as opy
from pandas import DataFrame

from time import sleep
api = opy.api.API()
UT = opy.objects.datatypes.UnixTime

api_obj_list = []
insts = [
     api.get_candles('AUD_CAD', 'M1', 500),
     api.get_candles('USD_CAD', 'M1', 500),
     api.get_candles('EUR_GBP', 'M1', 500),
     api.get_candles('AUD_JPY', 'M1', 500),
     api.get_candles('GBP_USD', 'M1', 500),
     api.get_candles('AUD_CHF', 'M1', 500),
]

for i in range(6):
    obj = opy.api.API()
    obj.load_accounts()
    obj.select_account()
    api_obj_list.append(obj)


while True:
    for i in range(len(insts)):
        cands = insts[i]
        altavd = opy.objects.indicators.AltAverageDifference(cands, on='open', period=120, name='altav', color='green')
        sma = opy.SMA(cands, on='open', period=120, name='sma', color='black')
        mavdiff = opy.objects.signals.AvDiffSignal(cands, [altavd, sma])
        api_obj_list[i].trade_signal(cands.instrument, mavdiff, cands[-1].close)
        insts[i] = api.get_candles(insts[i].instrument,'M1', 500)
        sleep(10)
