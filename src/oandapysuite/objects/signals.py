import decimal

from pandas import DataFrame

from oandapysuite.objects.instrument import CandleCluster

from decimal import Decimal


class BaseSignal:

    def sig_algorithm(self, candle_cluster: CandleCluster, parameters: list) -> DataFrame:
        return None


    def __init__(self, candle_cluster, parameters):
        self.data = self.sig_algorithm(candle_cluster, parameters)


class AvDiffSignal(BaseSignal):

    def sig_algorithm(self, candle_cluster: CandleCluster, params: list) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'name']
        self.in_position = False
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        period = params[0].period
        datapoints = []

        for i in range(len(candle_cluster)):
            if i < (period * 2) :
                datapoints.append(None)
                continue
            avdiff = params[0].data.iloc[i]['y']
            sma = params[1].data.iloc[i]['y']
            period_min = min([val for val in params[0].data['y'].tolist() if val is not None][i-period:i])
            period_max = max([val for val in params[0].data['y'].tolist() if val is not None][i-period:i])
            this_cand = candle_cluster[i].close
            if self.in_position == False:
                if ( avdiff <= period_min and this_cand < sma - Decimal(0.0015)):
                    datapoints.append(1)
                    self.in_position = 1
                    self.entry_price = candle_cluster[i].close
                    self.stop_loss = this_cand + avdiff * Decimal(1.5)
                    self.take_profit = this_cand - (avdiff) * Decimal(1)
                elif ( avdiff >= period_max and this_cand > sma + Decimal(0.0015)):
                    datapoints.append(3)
                    self.in_position = 3
                    self.entry_price = candle_cluster[i].close
                    self.stop_loss = this_cand + avdiff * Decimal(1.5)
                    self.take_profit = this_cand - (avdiff) * Decimal(1)
                else:
                    datapoints.append(0)
            elif self.in_position != False:
                    #Take profit             #Stop loss
                if ((this_cand >= self.take_profit or this_cand <= self.stop_loss)  and self.in_position == 1):
                    datapoints.append(2)
                    self.in_position = False
                elif ((this_cand <= self.take_profit or this_cand >= self.stop_loss)  and self.in_position == 3):
                    datapoints.append(4)
                    self.in_position = False
                else:
                    datapoints.append(0)
        return DataFrame(
            data={
                'x' : candle_cluster.history('time'),
                'y' : datapoints
            }
        )

