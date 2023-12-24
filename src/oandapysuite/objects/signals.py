import decimal

from pandas import DataFrame, Series
from numpy import nan, isnan

from oandapysuite.objects.instrument import CandleCluster

from decimal import Decimal


class BaseSignal:

    def _validate_indicators(self, indicators: dict):
        if not all([required_indicator in indicators.keys() for required_indicator in self.required_indicators]):
            raise IndicatorOptionsError(f'{self.__class__.__name__}, requires the options {" "}{" ".join(list(self.required_options.keys()))}')

    def __init__(self, **indicators):
        self._validate_indicators(indicators)
        for indicator, indicator_obj in indicators.items():
            setattr(self, indicator, indicator_obj)
        self.in_position = False
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        for key, value in indicators.items():
            setattr(self, key, value)


class AvDiffSignal(BaseSignal):

    def get_signal(self, candle: CandleCluster.Candle, indicator_index: int = None, cluster: CandleCluster = None) -> DataFrame:
        if indicator_index and indicator_index < self.max_period:
            return 0
        pass
        if cluster:
            self.avdiff.update(cluster)
            self.zscore.update(cluster)
        ind = indicator_index or -1
        rolling_avdiff = self.avdiff.data['y'].rolling(self.avdiff.period)
        rolling_zscore = self.zscore.data['y'].rolling(self.zscore.period)
        avdiff = self.avdiff.data.iloc[ind]['y']
        zscore = self.zscore.data.iloc[ind]['y']
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

    def __init__(self, **indicators):
        self.required_indicators = ['avdiff', 'zscore']
        super().__init__(**indicators)
        self.max_period = max([indicator.period for indicator in indicators.values()])
        self.min_period = min([indicator.period for indicator in indicators.values()])

class PAZATR(BaseSignal):

    def __get_entry_long_signal(self, rolling_psar, atr, zscore, ema_short, ema_long):
        last_10_candles_above_psar = rolling_psar.apply(lambda x: not isnan(x.iloc[-1])).all()
        atr_above_1_pip = atr > 0.00015
        ema_short_above_ema_long = ema_short > ema_long
        zscore_above_1_5 = abs(zscore) > 2.5
        pass
        return all([last_10_candles_above_psar, atr_above_1_pip, ema_short_above_ema_long, zscore_above_1_5])

    def __get_entry_short_signal(self, rolling_psar, atr, zscore, ema_short, ema_long):
        last_10_candles_below_psar = rolling_psar.apply(lambda x: not isnan(x.iloc[-1])).all()
        atr_above_1_pip = atr > 0.0001
        ema_short_below_ema_long = ema_short < ema_long
        zscore_above_1_5 = abs(zscore) > 1.5
        pass
        return all([last_10_candles_below_psar, atr_above_1_pip, ema_short_below_ema_long, zscore_above_1_5])

    def __get_exit_long_signal(self, ema_short, ema_long):
        ema_short_below_ema_long = ema_short < ema_long
        pass
        return ema_short_below_ema_long

    def __get_exit_short_signal(self, ema_short, ema_long):
        ema_short_above_ema_long = ema_short > ema_long
        pass
        return ema_short_above_ema_long

    def get_signal(self, candle: CandleCluster.Candle, indicator_index: int = None, cluster: CandleCluster = None) -> DataFrame:
        if indicator_index and indicator_index < self.max_period:
            return 0
        pass
        if cluster:
            self.psar.update(cluster)
            self.zscore.update(cluster)
            self.atr.update(cluster)
            self.ema_short.update(cluster)
            self.ema_long.update(cluster)
        ind = indicator_index or -1
        rolling_psar_up = self.psar.data['y2'].iloc[:ind].rolling(10)
        rolling_psar_down = self.psar.data['y1'].iloc[:ind].rolling(10)
        zscore = self.zscore.data.iloc[ind]['y']
        atr = self.atr.data.iloc[ind]['y']
        ema_short = self.ema_short.data['y'].iloc[ind]
        ema_long = self.ema_long.data['y'].iloc[ind]
        this_cand = candle.close
        if not self.in_position:
            entry_signal_long = self.__get_entry_long_signal(rolling_psar_up, atr, zscore, ema_short, ema_long)
            entry_signal_short = self.__get_entry_short_signal(rolling_psar_down, atr, zscore, ema_short, ema_long)
            if entry_signal_long:
                self.in_position = 1
                self.entry_price = this_cand
                return 1
            elif entry_signal_short:
                self.in_position = 3
                self.entry_price = this_cand
                return 3
            else:
                return 0
        elif self.in_position:
            exit_signal_long = self.__get_exit_long_signal(ema_short, ema_long)
            exit_signal_short = self.__get_exit_short_signal(ema_short, ema_long)
                # Take profit             Stop loss
            if exit_signal_long and self.in_position == 1:
                self.in_position = False
                return 2
            elif exit_signal_short and self.in_position == 3:
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

    def __init__(self, **indicators):
        self.required_indicators = ['psar', 'zscore', 'atr', 'ema_short', 'ema_long']
        super().__init__(**indicators)

        self.max_period = max([indicator.period for indicator in indicators.values() if hasattr(indicator, 'period')])
        self.min_period = min([indicator.period for indicator in indicators.values() if hasattr(indicator, 'period')])






