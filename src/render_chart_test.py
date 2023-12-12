import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('AUD_USD', 'M1', count=5000)
    print(candles.to_dataframe())


    avg_50day = opy.SMA(on='close', period=60, color='purple', name='sma 60')
    avg_500day = opy.SMA(on='close', period=200, color='blue', name='sma 200')
    rsi = opy.objects.indicators.RelativeStrengthIndex(on='close', period=30, color='orange', name='rsi')
#    stdforprice = opy.objects.indicators.SampleStandardDeviation(on='close', period=30, color='orange', name='std 60')
    zscore = opy.objects.indicators.ZScoreOfPrice(on='close', period=30, color='black', name='zscore')
#    std = opy.objects.indicators.SampleStandardDeviation(on='close', period=30, color='red', name='std')
#    bollinger = opy.objects.indicators.BollingerBands(std, on='close', period=30, color='green', name='bollinger')
    avg = opy.objects.indicators.AverageDifference(period=30, on='open', name='altav', color='black')
    avg_50day.update(candles)
    avg_500day.update(candles)
    avg.update(candles)
    rsi.update(candles)
    zscore.update(candles)
    avdiff_signal = opy.objects.signals.AvDiffSignal([avg, avg_50day, zscore])
#    sigs = avdiff_signal.generate_signals_for_candle_cluster(candles)


    api.initialize_chart(candles)
#    api.add_indicator(altavg)
#    api.add_indicator(std60)
#    api.add_indicator(zscore)
    api.add_indicator(rsi)
    api.add_indicator(avg)
    api.add_indicator(zscore)

    api.add_indicator(avg_50day)
    api.add_indicator(avg_500day)
#    api.add_indicator(bollinger)
    """
        for index, point in sigs.iterrows():
            if point['y'] == 1:
                api.fig.add_vline(x=point['x'], line_color="green")
            if point['y'] == 2:
                api.fig.add_vline(x=point['x'], line_width=3, line_dash="dash", line_color="green")
            if point['y'] == 3:
                api.fig.add_vline(x=point['x'], line_color="red")
            if point['y'] == 4:
                api.fig.add_vline(x=point['x'], line_width=3, line_dash="dash", line_color="red")
        pass
    """
    api.render_chart()

if __name__ == "__main__":
    main()
