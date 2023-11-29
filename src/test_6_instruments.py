import oandapysuite as opy
from pandas import DataFrame

from time import sleep

if __name__ == "__main__":
    api = opy.api.API()
    UT = opy.objects.datatypes.UnixTime

    api_obj_list = []
    insts = [
         api.get_candles('AUD_CAD', 'M1', 500),
         api.get_candles('USD_CAD', 'M1', 500),
         api.get_candles('EUR_GBP', 'M1', 500),
         api.get_candles('AUD_JPY', 'M1', 500),
         api.get_candles('GBP_USD', 'M1', 500),
         api.get_candles('AUD_CHF', 'M1', 500),
    ]

    for i in range(6):
        obj = opy.api.API()
        obj.load_accounts()
        obj.select_account()
        api_obj_list.append(obj)

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

            cands = insts[i]
            api_obj = api_obj_list[i]
            altavd = opy.objects.indicators.AverageDifference(cands, on='open', period=120, name='altav', color='green')
            sma = opy.SMA(cands, on='open', period=120, name='sma', color='black')
            mavdiff = opy.objects.signals.AvDiffSignal(cands, [altavd, sma])
            api_obj.trade_signal(cands.instrument, mavdiff, cands[-1].close)
            insts[i] = api.get_candles(insts[i].instrument,'M1', 500)
            sleep(10)
