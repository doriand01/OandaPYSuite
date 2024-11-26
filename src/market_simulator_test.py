import oandapysuite
import cProfile

def main():
    ins = input("What instrument do you want to trade:")
    gran = input("What timeframe do you want to trade:")
    count = input("How many candles:")
    api = oandapysuite.api.API()
    c = api.get_candles(ins, gran, int(count))
    ema_9 = oandapysuite.objects.indicators.trend.ExponentialMovingAverage(on='close', period=9, color='red', name='ema_long')
    ema_24 = oandapysuite.objects.indicators.trend.ExponentialMovingAverage(on='close', period=12, color='black', name='ema_mid')
    bollinger = oandapysuite.objects.indicators.volatility.BollingerBands(on='close', period=24, std=.6, name='bollinger')
    atr = oandapysuite.objects.indicators.volatility.AverageTrueRange(period=12)
    signal = oandapysuite.objects.signals.SignalFromXML("C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\DorandaPy\\src\\testxml.xml")
    sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=2000, ticks_per_second=40, signal=signal)
    sim.run()
    print(sim.trades)

if __name__ == '__main__':
    main()