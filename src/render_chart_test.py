import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

def main():
    UT = opy.objects.datatypes.UnixTime


    api = opy.api.API()

    candles = api.get_candles('USD_CAD', 'M1', count=5000)
    avg_200day = opy.SMA(on='close', period=200, color='purple', name='sma 200')
    altavg = opy.objects.indicators.AltAverageDifference(period=100, on='open', name='altav', color='black')
    AVDIFF = opy.objects.signals.AvDiffSignal()
    sigs = []
    for candle in candles.candles:
        avg_200day.add_candle(candle)
        altavg.add_candle(candle)
        sigs.append(AVDIFF.get_signal(candle, [altavg, avg_200day]))

    sigdict = dict(zip(candles.history('time'), sigs))
    api.initialize_chart(candles)
    api.add_indicator(altavg)
    api.add_indicator(avg_200day)
    for index, point in sigdict.items():
        if point == 1:
            api.fig.add_vline(x=index, line_color="green")
        if point == 2:
            api.fig.add_vline(x=index, line_width=3, line_dash="dash", line_color="green")
        if point == 3:
            api.fig.add_vline(x=index, line_color="red")
        if point == 4:
            api.fig.add_vline(x=index, line_width=3, line_dash="dash", line_color="red")
    api.render_chart()

if __name__ == "__main__":
    main()