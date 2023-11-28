import oandapysuite

ins = input("What instrument do you want to trade:")
gran = input("What timeframe do you want to trade:")
count = input("How many candles:")
api = oandapysuite.api.API()
c = api.get_candles(ins, gran, int(count))
sma = oandapysuite.SMA(on='close', period=50, color='purple', name='sma 100')
avdiff = oandapysuite.objects.indicators.AltAverageDifference(period=25, on='open', name='altav', color='black')
signal = oandapysuite.objects.signals.AvDiffSignal()
sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=650, ticks_per_second=600, generate_for='M1', signal=signal, indicators=[sma, avdiff])
sim.run()
print(sim.trades)