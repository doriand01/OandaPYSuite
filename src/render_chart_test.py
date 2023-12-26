import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('AUD_USD', 'M1', count=4000)
    print(candles.to_dataframe())
    williamsr = opy.objects.indicators.momentum.WilliamsR(period=14, name='williamsr', color='red')
    williamsr.update(candles)
    api.initialize_chart(candles)
    api.add_indicator(williamsr)

    '''
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
    '''

    api.render_chart()

if __name__ == "__main__":
    main()
