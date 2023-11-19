import oandapysuite


api = oandapysuite.api.API()
candles = api.get_candles('EUR_CHF', 'M1', _from='2012-11-16 00:00', to='2012-11-16 06:00')
sstdvn = oandapysuite.objects.indicators.SampleStandardDeviation(candles, on='open', period=20, color='green', z=-2, name='2z std')
sstdvp = oandapysuite.objects.indicators.SampleStandardDeviation(candles, on='open', period=20, color='green', z=2, name='2z std')
pstdvn = oandapysuite.objects.indicators.PopulationStandardDeviation(candles, on='open', color='red', z=2, name='popstd')
pstdvp  =oandapysuite.objects.indicators.PopulationStandardDeviation(candles, on='open', color='red', z=-2, name='popstd')

api.initialize_chart(candles)
api.add_indicator(sstdvn)
api.add_indicator(sstdvp)
api.add_indicator(pstdvn)
api.add_indicator(pstdvp)
api.render_chart()