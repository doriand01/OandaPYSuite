import decimal

from pandas import DataFrame

from oandapysuite.objects.instrument import CandleCluster

from decimal import Decimal


class BaseSignal:

    def sig_algorithm(self, candle_cluster: CandleCluster, parameters: list) -> DataFrame:
        return None

    def __init__(self, **options):
        self.in_position = False
        self.valid_options = ['on', 'period', 'color', 'name']
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        for key, value in options.items():
            setattr(self, key, value)

class AvDiffSignal(BaseSignal):

    def get_signal(self, candle: CandleCluster.Candle, params: list) -> DataFrame:
        period = params[0].period
        datapoints = []
        avdiff = params[0].data.iloc[-1]['y']
        sma = params[1].data.iloc[-1]['y']
        if not sma: return 0
        period_min = min([val for val in params[0].data['y'].tolist() if val is not None][-period:])
        period_max = max([val for val in params[0].data['y'].tolist() if val is not None][-period:])
        this_cand = candle.close
        if not self.in_position:
            if avdiff <= period_min and this_cand < sma - Decimal(0.0005):
                self.entry_price = candle.close
                self.stop_loss = this_cand + avdiff * Decimal(1.2)
                self.take_profit = this_cand - avdiff * Decimal(1.1)
                self.in_position = 1
                return 1
            elif avdiff >= period_max and this_cand > sma + Decimal(0.0005):
                self.entry_price = candle.close
                self.stop_loss = this_cand + avdiff * Decimal(1.2)
                self.take_profit = this_cand - avdiff * Decimal(1.1)
                self.in_position = 3
                return 3
            else:
                return 0
        elif self.in_position != False:
                # Take profit             Stop loss
            if (this_cand >= self.take_profit or this_cand <= self.stop_loss)  and self.in_position == 1:
                self.in_position = False
                return 2
            elif (this_cand <= self.take_profit or this_cand >= self.stop_loss)  and self.in_position == 3:
                self.in_position = False
                return 4
            else:
                return 0

