import oandapysuite as opy
import sys
print(sys.path)

a = opy.api.API()
b = a.get_candles('GBP_USD', 'M5', count=24)
print("hi")