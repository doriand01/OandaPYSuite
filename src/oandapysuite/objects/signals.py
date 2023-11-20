from pandas import DataFrame

from oandapysuite.objects.instrument import CandleCluster

from decimal import Decimal

class BaseSignal:

    def sig_algorithm(self, candle_cluster: CandleCluster, parameters: list) -> DataFrame:
        return None


    def __init__(self, candle_cluster, parameters):
        self.data = self.sig_algorithm(candle_cluster, parameters)


class MAVDIFFSignal(BaseSignal):

    def sig_algorithm(self, candle_cluster: CandleCluster, params: list) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'name']
        self.in_position = False
        datapoints = []
        for i in range(len(candle_cluster)):
            if i < params[0].period:
                datapoints.append(None)
                continue
            this_cand = getattr(candle_cluster[i], params[0].on)
            if self.in_position == False:
                if ((this_cand + Decimal(0.0001)) < params[0].data.iloc[i]['y'] and
                    this_cand > params[1].data.iloc[i]['y'] and
                    this_cand -Decimal(0.00025) > params[2].data.iloc[i]['y'] and
                    params[1].data.iloc[i]['y'] > params[2].data.iloc[i]['y']):
                    datapoints.append(1)
                    self.in_position = 1
                elif ((this_cand - Decimal(0.0001))> params[0].data.iloc[i]['y'] and
                    this_cand < params[1].data.iloc[i]['y'] and
                    this_cand + Decimal(0.00025)< params[2].data.iloc[i]['y'] and
                    params[1].data.iloc[i]['y'] < params[2].data.iloc[i]['y']):
                    datapoints.append(3)
                    self.in_position = 3
                else:
                    datapoints.append(0)
            elif self.in_position != False:
                if (this_cand < params[1].data.iloc[i]['y'] and self.in_position == 1):
                    datapoints.append(2)
                    self.in_position = False
                elif (this_cand > params[1].data.iloc[i]['y'] and self.in_position == 3):
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

