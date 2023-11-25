import oandapysuite as opy

from time import sleep

UT = opy.objects.datatypes.UnixTime


api = opy.api.API()
api.load_accounts()
api.select_account()

while True:
    cands = api.get_candles('USD_CAD', 'M1', 500)
    avg_200day = opy.SMA(cands, on='close', period=240, color='purple', name='sma 200')
    altavd = opy.objects.indicators.AltAverageDifference(cands, on='open', period=120, name='altav', color='green')
    mavdiff = opy.objects.signals.AvDiffSignal(cands, [altavd, avg_200day])
    api.trade_signal(cands.instrument, mavdiff   , cands[-1].close)
    sleep(5)
