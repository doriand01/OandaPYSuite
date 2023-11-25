import oandapysuite


api = oandapysuite.api.API()
c = api.get_candles('USD_CAD', 'H1', 12)
sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=3000, ticks_per_second=800, generate_for='M1', signal=oandapysuite.objects.signals.AvDiffSignal, indicators=[oandapysuite.SMA, oandapysuite.objects.indicators.AltAverageDifference])
sim.run()
pass