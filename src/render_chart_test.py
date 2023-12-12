import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('AUD_USD', 'M1', count=5000)
    print(candles.to_dataframe())
    boll_bands = opy.objects.indicators.BollingerBands(period=60, color='purple', name='bollinger bands')
    boll_bands.update(candles)
    api.initialize_chart(candles, type='ohlc')
    api.add_indicator(boll_bands)
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
