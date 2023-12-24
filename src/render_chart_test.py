import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('AUD_USD', 'M1', count=4000)
    print(candles.to_dataframe())
    psar = opy.objects.indicators.trend.ParabolicSAR(color='orange', name='parabolic sar', accel=0.0175, max=0.2)
    zscore = opy.objects.indicators.volatility.ZScoreOfPrice(on='close', period=24, color='black', name='zscore')
    atr = opy.objects.indicators.volatility.AverageTrueRange(period=9, color='black', name='atr')
    atr.update(candles)
    psar.update(candles)
    ema = opy.objects.indicators.trend.ExponentialMovingAverage(on='close', period=9, color='blue', name='ema 9')
    ema2 = opy.objects.indicators.trend.ExponentialMovingAverage(on='close', period=24, color='purple', name='ema 24')
    ema.update(candles)
    ema2.update(candles)
    zscore.update(candles)
    pazatr = opy.objects.signals.PAZATR(psar=psar, zscore=zscore, atr=atr, ema_short=ema, ema_long=ema2)
    sigs = pazatr.generate_signals_for_candle_cluster(candles)
    api.initialize_chart(candles)
    api.add_indicator(zscore)
    api.add_indicator(atr)
    api.add_indicator(psar)
    api.add_indicator(ema)
    api.add_indicator(ema2)

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

    api.render_chart()

if __name__ == "__main__":
    main()
