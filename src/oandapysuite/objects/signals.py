import decimal

from pandas import DataFrame
from numpy import nan

from oandapysuite.objects.instrument import CandleCluster

from decimal import Decimal


class BaseSignal:

    def __init__(self, **options):
        self.in_position = False
        self.valid_options = ['on', 'period', 'color', 'name']
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        for key, value in options.items():
            setattr(self, key, value)


class AvDiffSignal(BaseSignal):

    def get_signal(self, candle: CandleCluster.Candle, indicator_index: int = None) -> DataFrame:
        if indicator_index and indicator_index < self.period:
            return 0
        ind = indicator_index or -1
        rolling_avdiff = self.params[0].data['y'].rolling(self.params[0].period)
        rolling_zscore = self.params[2].data['y'].rolling(self.params[2].period)
        avdiff = self.params[0].data.iloc[ind]['y']
        zscore = self.params[2].data.iloc[ind]['y']
        avdiff_period_min = rolling_avdiff.min().iloc[ind]
        avdiff_period_max = rolling_avdiff.max().iloc[ind]
        z_period_min = rolling_zscore.min().iloc[ind]
        z_period_max = rolling_zscore.max().iloc[ind]
        this_cand = candle.close
        if not self.in_position:
            if avdiff <= avdiff_period_min and zscore >= z_period_max and zscore > 2.5:
                self.in_position = 1
                self.entry_price = this_cand
                self.stop_loss = this_cand - Decimal(abs(avdiff)) * 2
                self.take_profit = this_cand + Decimal(abs(avdiff))
                return 1
            elif avdiff >= avdiff_period_max and zscore <= z_period_min and zscore > 2.5:
                self.in_position = 3
                self.entry_price = this_cand
                self.stop_loss = this_cand + Decimal(abs(avdiff)) * 2
                self.take_profit = this_cand - Decimal(abs(avdiff))
                return 3
            else:
                return 0
        elif self.in_position:
                # Take profit             Stop loss
            if (this_cand >= self.take_profit or this_cand <= self.stop_loss) and self.in_position == 1:
                self.in_position = False
                return 2
            elif (this_cand <= self.take_profit or this_cand >= self.stop_loss) and self.in_position == 3:
                self.in_position = False
                return 4
            else:
                return 0

    def generate_signals_for_candle_cluster(self, candles: CandleCluster) -> list:
        signals = []
        for i in range(len(candles)):
            candle = candles[i]
            signals.append(self.get_signal(candle, indicator_index=i))
        return DataFrame(
            data={
                'x': candles.history('time'),
                'y': signals,
            }
        )

    def __init__(self, params: list, **options):
        super().__init__(**options)
        self.params = params
        self.period = max([param.period for param in params])

