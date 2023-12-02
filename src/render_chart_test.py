import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

def main():

    api = opy.api.API()

    candles = api.get_candles('USD_CAD', 'M1', count=2000)
    avg_50day = opy.SMA(on='close', period=120, color='purple', name='sma 60')
    avg_500day = opy.SMA(on='close', period=200, color='blue', name='sma 200')
    std60 = opy.objects.indicators.SampleStandardDeviation(on='close', period=120, color='orange', name='std 60')
    stdforprice = opy.objects.indicators.SampleStandardDeviation(on='close', period=120, color='orange', name='std 60')
    zscore = opy.objects.indicators.ZScoreOfPrice(stdforprice, on='close', period=120, color='black', name='zscore')
    std = opy.objects.indicators.SampleStandardDeviation(on='close', period=60, color='red', name='std')
    bollinger = opy.objects.indicators.BollingerBands(std, on='close', period=60, color='green', name='bollinger')
    altavg = opy.objects.indicators.AverageDifference(period=60, on='open', name='altav', color='black')
    AVDIFF = opy.objects.signals.AvDiffSignal()
    sigs = []
    for candle in candles.candles:
        avg_50day.add_candle(candle)
        avg_500day.add_candle(candle)
        std60.add_candle(candle)
        zscore.add_candle(candle)
        altavg.add_candle(candle)
        bollinger.add_candle(candle)
        sigs.append(AVDIFF.get_signal(candle, [altavg, avg_50day, std60, zscore]))

    sigdict = dict(zip(candles.history('time'), sigs))
    api.initialize_chart(candles)
    api.add_indicator(altavg)
    api.add_indicator(std60)
    api.add_indicator(zscore)
    api.add_indicator(avg_50day)
    api.add_indicator(avg_500day)
    api.add_indicator(bollinger)
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