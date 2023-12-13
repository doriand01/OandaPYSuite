import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('AUD_USD', 'M1', count=2000)
    print(candles.to_dataframe())
    psar = opy.objects.indicators.trend.ParabolicSAR(color='orange', name='parabolic sar', accel=0.02, max=0.2)
    zscore = opy.objects.indicators.volatility.ZScoreOfPrice(on='close', period=60, color='black', name='zscore')
    std = opy.objects.indicators.volatility.SampleStandardDeviation(on='close', period=60, color='red', name='std 60')
    psar.update(candles)
    zscore.update(candles)
    std.update(candles)
    api.initialize_chart(candles)
    api.add_indicator(zscore)
    api.add_indicator(std)
    api.add_indicator(psar)
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
