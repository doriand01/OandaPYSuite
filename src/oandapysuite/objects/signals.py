import decimal

from pandas import DataFrame, Series
from numpy import nan, isnan

from math import e

from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.exceptions import *
from oandapysuite.settings import INDICATOR_ALIASES

from decimal import Decimal
from collections import deque
from xml.etree import ElementTree as ET

import importlib


decimal.getcontext().prec = 5


class BaseSignal:

    def _check_stop_loss(self, current_price):
        if self.in_position == 1 and current_price <= self.stop_loss:
            self.in_position = False
            return 2
        elif self.in_position == 3 and current_price >= self.stop_loss:
            self.in_position = False
            return 4
        else:
            return 0

    def _validate_indicators(self, indicators: dict):
        if not all([required_indicator in indicators.keys() for required_indicator in self.required_indicators]):
            raise IndicatorOptionsError(f'{self.__class__.__name__}, requires the options {" "}{" ".join(list(self.required_indicators))}')

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

class LogicalUnit:

    def __init__(self, conditions):
        self.conditions = []
        for condition in conditions:
            i = 1
            self.conditions.append({
                'type': condition.attrib['type'],
                'left': condition.find('LeftOperand').attrib['id'],
                'right': condition.find('RightOperand').attrib['id'],
            })

    def evaluate(self, indicators, price):
        all_conditions = []
        for condition in self.conditions:
            if condition['left'] == 'price':
                left = price
                right = indicators[condition['right']].data['y'].iloc[-1]
            elif condition['right'] == 'price':
                left = indicators[condition['left']].data['y'].iloc[-1]
                right = price
            else:
                left = indicators[condition['left']].data['y'].iloc[-1]
                right = indicators[condition['right']].data['y'].iloc[-1]
            if condition['type'] == 'GreaterThan':
                all_conditions.append(left > right)
            elif condition['type'] == 'LessThan':
                all_conditions.append(left < right)
            elif condition['type'] == 'Equals':
                all_conditions.append(left == right)
        return all(all_conditions)


class SignalFromXML(BaseSignal):


    def _get_indicators(self, indicators):
        indicators_dict = {}
        for indicator in indicators:
            settings_dict = {}
            indicator_class = getattr(importlib.import_module(INDICATOR_ALIASES[indicator.attrib['name']].rsplit('.', 1)[0]), indicator.attrib['name'])
            self.indicators_list.append(indicator.attrib['id'])
            settings = indicator.findall('Setting')
            for setting in settings:
                if any(char.isdigit() for char in setting.text):
                    settings_dict[setting.attrib['name']] = float(setting.text)
                else:
                    settings_dict[setting.attrib['name']] = setting.text
            indicator_object = indicator_class(**settings_dict)
            indicators_dict[indicator.attrib['id']] = indicator_object
        return indicators_dict

    def _build_logical_units(self, logical_units):
        for unit in logical_units:
            conditions = unit.findall('Condition')
            logical_unit = LogicalUnit(conditions)
            setattr(self, unit.attrib['id'], logical_unit)

    def __init__(self, xml):
        self.indicators_list = []
        self.required_indicators = []
        signal_xml = ET.parse(xml).getroot()
        self.entry_long = signal_xml.find('EntryLong')
        self.entry_short = signal_xml.find('EntryShort')
        self.exit_long = signal_xml.find('ExitLong')
        self.exit_short = signal_xml.find('ExitShort')
        self._build_logical_units(signal_xml.findall('LogicalUnit'))
        indicators = signal_xml.findall('Indicator')
        indicators = self._get_indicators(indicators)
        super().__init__(**indicators)
        self.max_period = max([indicator.period for indicator in indicators.values() if hasattr(indicator, 'period')])

    def __get_entry_long_signal(self, price):
        unit_states = []
        entry_units = list(self.entry_long)
        for unit in entry_units:
            logical_unit = getattr(self, unit.attrib['id'])
            indicator_dicts = {indicator: self.__dict__[indicator] for indicator in self.indicators_list}
            if unit.tag == 'True':
                unit_states.append(logical_unit.evaluate(indicator_dicts, price))
            elif unit.tag == 'False':
                unit_states.append(not logical_unit.evaluate(indicator_dicts, price))
        return all(unit_states)

    def __get_entry_short_signal(self, price):
        unit_states = []
        entry_units = list(self.entry_short)
        for unit in entry_units:
            logical_unit = getattr(self, unit.attrib['id'])
            indicator_dicts = {indicator: self.__dict__[indicator] for indicator in self.indicators_list}
            if unit.tag == 'True':
                unit_states.append(logical_unit.evaluate(indicator_dicts, price))
            elif unit.tag == 'False':
                unit_states.append(not logical_unit.evaluate(indicator_dicts, price))
        return all(unit_states)

    def __get_exit_long_signal(self, price):
        unit_states = []
        entry_units = list(self.exit_long)
        for unit in entry_units:
            logical_unit = getattr(self, unit.attrib['id'])
            indicator_dicts = {indicator: self.__dict__[indicator] for indicator in self.indicators_list}
            if unit.tag == 'True':
                unit_states.append(logical_unit.evaluate(indicator_dicts, price))
            elif unit.tag == 'False':
                unit_states.append(not logical_unit.evaluate(indicator_dicts, price))
        return all(unit_states)

    def __get_exit_short_signal(self, price):
        unit_states = []
        entry_units = list(self.exit_short)
        for unit in entry_units:
            logical_unit = getattr(self, unit.attrib['id'])
            indicator_dicts = {indicator: self.__dict__[indicator] for indicator in self.indicators_list}
            if unit.tag == 'True':
                unit_states.append(logical_unit.evaluate(indicator_dicts, price))
            elif unit.tag == 'False':
                unit_states.append(not logical_unit.evaluate(indicator_dicts, price))
        return all(unit_states)

    def get_signal(self, candle: CandleCluster.Candle, indicator_index: int = None, cluster: CandleCluster = None) -> DataFrame:
        if (indicator_index and indicator_index < self.max_period) or indicator_index == 0:
            return 0
        if cluster:
            for indicator in self.indicators_list:
                getattr(self, indicator).update(cluster)
        ind = indicator_index or -1
        if not self.in_position:
            if self.__get_entry_long_signal(candle.close):
                self.in_position = 1
                self.entry_price = candle.close
                return 1
            elif self.__get_entry_short_signal(candle.close):
                self.in_position = 3
                self.entry_price = candle.close
                return 3
            else:
                return 0
        elif self.in_position:
            if self.__get_exit_long_signal(candle.close) and self.in_position == 1:
                self.in_position = False
                return 2
            if self.__get_exit_short_signal(candle.close) and self.in_position == 3:
                self.in_position = False
                return 4



class EMACrossSignal(BaseSignal):

    def __init__(self, **indicators):
        self.required_indicators = []
        super().__init__(**indicators)
        self.max_period = max([indicator.period for indicator in indicators.values() if hasattr(indicator, 'period')])

    def __get_entry_long_signal(self, ema_9, ema_24):
        ema_24_below_ema_9 = ema_24 < ema_9
        diff_ema_above_25 = abs(ema_24-ema_9) > 0.00015
        return all([ema_24_below_ema_9, diff_ema_above_25])

    def __get_entry_short_signal(self, ema_9, ema_24):
        ema_24_above_ema_9 = ema_24 > ema_9
        diff_ema_above_25 = abs(ema_24-ema_9) > 0.00015
        return all([ema_24_above_ema_9, diff_ema_above_25])
    def __get_exit_long_signal(self, ema_9, ema_24):
        ema_24_above_ema_9 = ema_24 > ema_9
        return ema_24_above_ema_9

    def __get_exit_short_signal(self, ema_9, ema_24):
        ema_24_below_ema_9 = ema_24 < ema_9
        return ema_24_below_ema_9

    def get_signal(self, candle: CandleCluster.Candle, indicator_index: int = None, cluster: CandleCluster = None) -> DataFrame:
        if (indicator_index and indicator_index < self.max_period) or indicator_index == 0:
            return 0
        if cluster:
            self.ema_9.update(cluster)
            self.rsi.update(cluster)
            self.ema_24.update(cluster)
        ind = indicator_index or -1
        ema_9 = self.ema_9.data['y'].iloc[ind]
        ema_12 = self.ema_12.data['y'].iloc[ind]
        ema_24 = self.ema_24.data['y'].iloc[ind]
        this_cand = candle.close
        if not self.in_position:
            entry_signal_long = self.__get_entry_long_signal(ema_9, ema_24)
            entry_signal_short = self.__get_entry_short_signal(ema_9, ema_24)
            if entry_signal_long:
                self.in_position = 1
                self.entry_price = this_cand
                self.stop_loss = this_cand - 300
                return 1
            elif entry_signal_short:
                self.in_position = 3
                self.entry_price = this_cand
                self.stop_loss = this_cand + 300
                return 3
            else:
                return 0
        elif self.in_position:
            exit_signal_long = self.__get_exit_long_signal(ema_9, ema_12)
            exit_signal_short = self.__get_exit_short_signal(ema_9, ema_12)
                # Take profit             Stop loss
            if (exit_signal_long and self.in_position == 1) or (candle.time.weekday() == 4 and candle.time.hour >= 16):
                self.in_position = False
                self.stop_loss = 0
                return 2
            if (exit_signal_short and self.in_position == 3) or (candle.time.weekday() == 4 and candle.time.hour >= 16):
                self.in_position = False
                self.stop_loss = 0
                return 4
            else:
                return self._check_stop_loss(this_cand)

    def generate_signals_for_candle_cluster(self, candles: CandleCluster) -> list:
        signals = []
        for i in range(len(candles)):
            candle = candles[i]
            signals.append(self.get_signal(candle, indicator_index=i, cluster=candles))
        pass
        return DataFrame(
            data={
                'x': candles.history('time'),
                'y': signals,
            }
        )


class Boll2EMA(BaseSignal):

    def __init__(self, **indicators):
        self.required_indicators = []
        super().__init__(**indicators)
        self.max_period = max([indicator.period for indicator in indicators.values() if hasattr(indicator, 'period')])

    def _check_stop_loss(self, current_price):
        if self.in_position == 1 and current_price <= self.stop_loss:
            return True
        elif self.in_position == 3 and current_price >= self.stop_loss:
            return True
        else:
            return False

    def _check_take_profit(self, current_price):
        if self.in_position == 1 and current_price >= self.take_profit:
            return True
        elif self.in_position == 3 and current_price <= self.take_profit:
            return True
        else:
            return False

    def __get_entry_long_signal(self, bolllow, bollhigh, ema_9, ema_24, price):
        boll_diff_above_2 = abs(bollhigh - bolllow) > 0.0002
        price_above_bollhigh = price > ema_9 > ema_24 > bollhigh
        return all([price_above_bollhigh, boll_diff_above_2])

    def __get_entry_short_signal(self, bollhigh, bolllow, ema_9, ema_24, price):
        boll_diff_above_2 = abs(bollhigh - bolllow) > 0.0002
        price_below_bolllow = price < ema_9 < ema_24 < bolllow
        return all([price_below_bolllow, boll_diff_above_2])

    def __get_exit_long_signal(self, ema_24, bollhigh):
        ema_24_below_bollhigh = ema_24 < bollhigh
        return ema_24_below_bollhigh

    def __get_exit_short_signal(self, ema_24, bolllow):
        ema_24_above_bolllow = ema_24 > bolllow
        return ema_24_above_bolllow

    def get_signal(self, candle: CandleCluster.Candle, indicator_index: int = None, cluster: CandleCluster = None) -> DataFrame:
        if (indicator_index and indicator_index < self.max_period) or indicator_index == 0:
            return 0
        if cluster:
            self.ema_9.update(cluster)
            self.ema_24.update(cluster)
            self.bollinger.update(cluster)
            self.atr.update(cluster)
        ind = indicator_index or -1
        ema_9 = self.ema_9.data['y'].iloc[ind]
        ema_24 = self.ema_24.data['y'].iloc[ind]
        bollhigh = Decimal(self.bollinger.data['y2'].iloc[ind])
        bolllow = Decimal(self.bollinger.data['y1'].iloc[ind])
        this_cand = candle.close
        if not self.in_position:
            if self.__get_entry_long_signal(bolllow, bollhigh, ema_9, ema_24, this_cand):
                self.in_position = 1
                self.entry_price = this_cand
                self.take_profit = this_cand + abs(bollhigh - bolllow) * Decimal(1.5)
                self.stop_loss = this_cand - abs(bollhigh - bolllow) * Decimal(0.7)
                return 1
            elif self.__get_entry_short_signal(bollhigh, bolllow, ema_9, ema_24, this_cand):
                self.in_position = 3
                self.entry_price = this_cand
                self.take_profit = this_cand - abs(bollhigh - bolllow) * Decimal(1.5)
                self.stop_loss = this_cand + abs(bollhigh - bolllow) * Decimal(0.7)
                return 3
            else:
                return 0
        elif self.in_position:
            if self.__get_exit_long_signal(ema_24, bollhigh) and self.in_position == 1:
                self.in_position = False
                return 2
            if self.__get_exit_short_signal(ema_24, bolllow) and self.in_position == 3:
                self.in_position = False
                return 4

    def generate_signals_for_candle_cluster(self, candles: CandleCluster) -> list:
        signals = []
        for i in range(len(candles)):
            candle = candles[i]
            signals.append(self.get_signal(candle, indicator_index=i, cluster=candles))
        pass
        return DataFrame(
            data={
                'x': candles.history('time'),
                'y': signals,
            }
        )














