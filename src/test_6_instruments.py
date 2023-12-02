import oandapysuite as opy
from pandas import DataFrame

from time import sleep

if __name__ == "__main__":
    api = opy.api.API()
    UT = opy.objects.datatypes.UnixTime

    api_obj_list = []
    insts = [
         api.get_candles('AUD_CAD', 'M1', 1),
         api.get_candles('USD_CAD', 'M1', 1),
         api.get_candles('EUR_GBP', 'M1', 1),
         api.get_candles('AUD_JPY', 'M1', 1),
         api.get_candles('GBP_USD', 'M1', 1),
         api.get_candles('AUD_CHF', 'M1', 1),
    ]

    inds = []

    for i in range(6):
        sma = opy.SMA(on='close', period=120, color='purple', name='sma 100')
        avdiff = opy.objects.indicators.AverageDifference(period=60, on='open', name='altav', color='black')
        stdforprice = opy.objects.indicators.SampleStandardDeviation(on='close', period=120, color='orange',
                                                                              name='std 60')
        zscore = opy.objects.indicators.ZScoreOfPrice(stdforprice, on='close', period=120, color='black',
                                                               name='zscore')
        inds.append([avdiff, sma, stdforprice, zscore])
        obj = opy.api.API()
        obj.load_accounts()
        obj.select_account()
        api_obj_list.append(obj)

    for cand_clust in insts:
        for cand in cand_clust:
            for ind in inds:
                for indicator in ind:
                    indicator.add_candle(cand)

    def plot_signal(signal, api_obj):
        for index, point in signal.data.iterrows():
            if point['y'] == 1:
                api_obj.fig.add_vline(x=point['x'], line_color="green")
            if point['y'] == 2:
                api_obj.fig.add_vline(x=point['x'], line_width=3, line_dash="dash", line_color="green")
            if point['y'] == 3:
                api_obj.fig.add_vline(x=point['x'], line_color="red")
            if point['y'] == 4:
                api_obj.fig.add_vline(x=point['x'], line_width=3, line_dash="dash", line_color="red")


    while True:
        for i in range(len(insts)):
            api_obj = api_obj_list[i]
            cands = api_obj.get_candles(insts[i].instrument, 'M1', 1)
            mavdiff = opy.objects.signals.AvDiffSignal()
            signal = mavdiff.get_signal(cands[-1], inds[i])
            api_obj.trade_signal(cands[-1].instrument, signal, cands[-1])
            sleep(10)
