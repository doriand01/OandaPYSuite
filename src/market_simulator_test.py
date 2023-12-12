import oandapysuite


def main():
    ins = input("What instrument do you want to trade:")
    gran = input("What timeframe do you want to trade:")
    count = input("How many candles:")
    api = oandapysuite.api.API()
    c = api.get_candles(ins, gran, int(count))
    sma = oandapysuite.SMA(on='close', period=30, color='purple', name='sma 100')
    avdiff = oandapysuite.objects.indicators.AverageDifference(period=15, on='open', name='altav', color='black')
    stdforprice = oandapysuite.objects.indicators.SampleStandardDeviation(on='close', period=30, color='orange', name='std 60')
    zscore = oandapysuite.objects.indicators.ZScoreOfPrice(on='close', period=30, color='black', name='zscore')
    signal = oandapysuite.objects.signals.AvDiffSignal([avdiff, sma, zscore])
    sim = oandapysuite.objects.trade.Backtester(c, api, speed_factor=3000, ticks_per_second=700, generate_for='M1', indicators=[avdiff, sma, zscore], signal=signal)
    sim.run()
    print(sim.trades)

if __name__ == '__main__':
    main()