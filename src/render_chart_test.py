import oandapysuite as opy
import oandapysuite.objects.indicators

from time import sleep
import cProfile

CC = opy.objects.instrument.CandleCluster

def main():

    api = opy.api.API()

    candles = api.get_candles('GBP_USD', 'M5', count=2500)
    ema_short = opy.objects.indicators.trend.ExponentialMovingAverage(on='close', period=9, name='ema_short')
    ema_long = opy.objects.indicators.trend.ExponentialMovingAverage(on='close', period=12, name='ema_long')
    ema_trend = opy.objects.indicators.trend.ExponentialMovingAverage(on='close', period=60, name='ema_trend')
    rsi = opy.objects.indicators.momentum.RelativeStrengthIndex(on='close', period=24)
    atr = opy.objects.indicators.volatility.AverageTrueRange(period=12)
    atr2 = opy.objects.indicators.volatility.AverageTrueRange(period=1)
    bollinger = opy.objects.indicators.volatility.BollingerBands(on='close', period=24, std=0.6, name='bollinger')
    boll2ema = opy.objects.signals.Boll2EMA(ema_9=ema_short, ema_24=ema_long, bollinger=bollinger, atr=atr)
    render_engine = opy.render.RenderEngine(candles)
    render_engine.add_indicator(ema_long)
    render_engine.add_indicator(ema_short)
    render_engine.add_indicator(bollinger)
    render_engine.add_indicator(rsi)

    render_engine.render_chart()


if __name__ == "__main__":
    main()
