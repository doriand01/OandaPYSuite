import oandapysuite

ins = input("What instrument do you want to trade:")
gran = input("What timeframe do you want to trade:")
count = input("How many candles:")
api = oandapysuite.api.API()
c = api.get_candles(ins, gran, int(count))
sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=650, ticks_per_second=600, generate_for='M1', signal=oandapysuite.objects.signals.AvDiffSignal, indicators=[oandapysuite.SMA, oandapysuite.objects.indicators.AltAverageDifference])
sim.run()
print(sim.trades)