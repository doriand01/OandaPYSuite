import oandapysuite


def main():
    ins = input("What instrument do you want to trade:")
    gran = input("What timeframe do you want to trade:")
    count = input("How many candles:")
    api = oandapysuite.api.API()
    c = api.get_candles(ins, gran, int(count))
    ema_long = oandapysuite.objects.indicators.trend.ExponentialMovingAverage(on='close', period=24, color='red', name='ema_long')
    ema_short = oandapysuite.objects.indicators.trend.ExponentialMovingAverage(on='close', period=9, color='blue', name='ema_short')
    zscore = oandapysuite.objects.indicators.volatility.ZScoreOfPrice(on='close', period=24, color='black', name='zscore')
    atr = oandapysuite.objects.indicators.volatility.AverageTrueRange(period=9, color='black', name='atr')
    psar = oandapysuite.objects.indicators.trend.ParabolicSAR(color='orange', name='parabolic sar', accel=0.0175, max=0.2)
    signal = oandapysuite.objects.signals.PAZATR(psar=psar, zscore=zscore, atr=atr, ema_short=ema_short, ema_long=ema_long)
    sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=3000, ticks_per_second=700, generate_for='M1', signal=signal)
    sim.run()
    print(sim.trades)

if __name__ == '__main__':
    main()