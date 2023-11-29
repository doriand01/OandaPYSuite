import oandapysuite

ins = input("What instrument do you want to trade:")
gran = input("What timeframe do you want to trade:")
count = input("How many candles:")
api = oandapysuite.api.API()
c = api.get_candles(ins, gran, int(count))
sma = oandapysuite.SMA(on='close', period=30, color='purple', name='sma 100')
avdiff = oandapysuite.objects.indicators.AverageDifference(period=15, on='open', name='altav', color='black')
signal = oandapysuite.objects.signals.AvDiffSignal()
sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=800, ticks_per_second=700, generate_for='M1', signal=signal, indicators=[avdiff, sma])
sim.run()
print(sim.trades)