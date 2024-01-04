import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('USD_CAD', 'M1', count=500)
    macd = opy.objects.indicators.trend.MovingAverageConvergenceDivergence(on='close', period_slow=26, period_fast=12, period_signal=9, name='macd')
    ema = opy.objects.indicators.trend.ExponentialMovingAverage(on='close', period=24, color='blue', name='ema')
    psar = opy.objects.indicators.trend.ParabolicSAR(color='orange', name='parabolic sar', accel=0.0175, max=0.2)
    atr = opy.objects.indicators.volatility.AverageTrueRange(period=5, color='black', name='atr')
    render_engine = opy.render.RenderEngine(candles)
    render_engine.add_indicator(macd)
    render_engine.add_indicator(ema)
    render_engine.add_indicator(psar)
    render_engine.add_indicator(atr)
    render_engine.render_chart()

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

if __name__ == "__main__":
    main()
