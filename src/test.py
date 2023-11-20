import oandapysuite as opy


api = opy.api.API()
candles = api.get_candles('USD_CAD', 'M1', _from='2023 10 31 00:00', to='2023 11 1 00:00')
avg_10day = opy.SMA(candles, on='close', period=10, color='purple', name='10 day sma')
avg_20day = opy.SMA(candles, on='close', period=20,color='green', name='sma 20')
ad50 = opy.objects.indicators.AverageDifference(candles, on='close', period=50, color='black', name='avgdiff')
ad20 = opy.objects.indicators.AverageDifference(candles, on='close', period=20, color='gray', name='avgdiff')

#MAVDIFF = opy.objects.signals.MAVDIFFSignal(candles, [avg_diff_15day, avg_10day, avg_20day])
api.initialize_chart(candles)
api.add_indicator(ad50)
api.add_indicator(ad20)
api.add_indicator(avg_20day)
api.add_indicator(avg_10day)
"""
for index,point in MAVDIFF.data.iterrows():
    if point['y'] == 1:
        api.fig.add_vline(x=point['x'], line_color="green")
    if point['y'] == 2:
        api.fig.add_vline(x=point['x'],line_width=3, line_dash="dash", line_color="green")
    if point['y'] == 3:
        api.fig.add_vline(x=point['x'], line_color="red")
    if point['y'] == 4:
        api.fig.add_vline(x=point['x'],line_width=3, line_dash="dash", line_color="red")
"""

api.render_chart()