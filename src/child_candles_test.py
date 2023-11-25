import oandapysuite as opy

from time import sleep

UT = opy.objects.datatypes.UnixTime


api = opy.api.API()
cands = api.get_candles('USD_CAD', 'M1', _from=UT('2023-11-15'), to=UT('2023-11-15 00:10'))
children = api.get_child_candles(cands[-1],'S5')


