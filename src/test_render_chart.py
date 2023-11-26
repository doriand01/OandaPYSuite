import oandapysuite as opy

from time import sleep

UT = opy.objects.datatypes.UnixTime


api = opy.api.API()

candles = api.get_candles('EUR_USD', 'M1', count=5000)
avg_200day = opy.SMA(candles, on='close', period=200, color='purple', name='sma 200')
avg_9day = opy.SMA(candles, on='close', period=100,color='green', name='sma 9')
altavg = opy.objects.indicators.AltAverageDifference(candles, period=100, on='open', name='altav', color='black')
rsi = opy.objects.indicators.RelativeStrengthIndex(candles, on='close', period=100, name='rsi', color='black')


AVDIFF = opy.objects.signals.AvDiffSignal(candles, [altavg,avg_200day])
api.initialize_chart(candles)
api.add_indicator(altavg)
api.add_indicator(rsi)
api.add_indicator(avg_200day)
api.add_indicator(avg_9day)

for index,point in AVDIFF.data.iterrows():
    if point['y'] == 1:
        api.fig.add_vline(x=point['x'], line_color="green")
    if point['y'] == 2:
        api.fig.add_vline(x=point['x'],line_width=3, line_dash="dash", line_color="green")
    if point['y'] == 3:
        api.fig.add_vline(x=point['x'], line_color="red")
    if point['y'] == 4:
        api.fig.add_vline(x=point['x'],line_width=3, line_dash="dash", line_color="red")


api.render_chart()