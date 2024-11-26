import oandapysuite as opy

api = opy.api.API()
cands = api.get_candles('GBP_USD', 'M5', count=4600)
b = opy.objects.signals.find_legs(cands, 10)
print(b)