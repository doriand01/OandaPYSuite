from pandas import DataFrame, Series
from numpy import nan, isnan

from math import e

from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.exceptions import *
from oandapysuite.settings import INDICATOR_ALIASES
from oandapysuite.utils import to_float_or_int_or_str as tfis

from collections import deque
from xml.etree import ElementTree as ET

import importlib




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
            self.conditions.append({
                'type': condition.attrib['type'],
                'left': condition.find('LeftOperand').attrib['id'],
                'right': condition.find('RightOperand').attrib['id'],
            })

            if 'select' in condition.find('LeftOperand').attrib.keys():
                self.conditions[-1]['left_select'] = condition.find('LeftOperand').attrib['select']

            if 'select' in condition.find('RightOperand').attrib.keys():
                self.conditions[-1]['right_select'] = condition.find('RightOperand').attrib['select']

    def evaluate(self, indicators, price, indicator_index = None):
        all_conditions = []
        indicator_index = indicator_index or -1
        for condition in self.conditions:
            left_selected = condition['left_select'] if 'left_select' in condition.keys() else 'y'
            right_selected = condition['right_select'] if 'right_select' in condition.keys() else 'y'
            if condition['left'] == 'price':
                left = price
                right = getattr(indicators[condition['right']], right_selected)[indicator_index]
            elif condition['right'] == 'price':
                left = getattr(indicators[condition['left']], left_selected)[indicator_index]
                right = price
            else:
                left = getattr(indicators[condition['left']], left_selected)[indicator_index]
                right = getattr(indicators[condition['right']], right_selected)[indicator_index]
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
                settings_dict[setting.attrib['name']] = tfis(setting.text)
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

    def __evaluate_signal(self, signal, price):
        unit_states = []
        entry_units = list(getattr(self, signal))
        for unit in entry_units:
            logical_unit = getattr(self, unit.attrib['id'])
            indicator_dicts = {indicator: self.__dict__[indicator] for indicator in self.indicators_list}
            if unit.tag == 'True':
                unit_states.append(logical_unit.evaluate(indicator_dicts, price))
            elif unit.tag == 'False':
                unit_states.append(not logical_unit.evaluate(indicator_dicts, price))
        return all(unit_states)

    def get_signal(self, price, indicator_index: int = None, cluster=None):
        if (indicator_index and indicator_index < self.max_period) or indicator_index == 0:
            return 0
        for indicator in self.indicators_list:
            getattr(self, indicator).update(cluster)
        ind = indicator_index or -1
        if not self.in_position:
            if self.__evaluate_signal('entry_long', price):
                self.in_position = 1
                self.entry_price = price
                return 1
            elif self.__evaluate_signal('entry_short', price):
                self.in_position = 3
                self.entry_price = price
                return 3
            else:
                return 0
        elif self.in_position:
            if self.__evaluate_signal('exit_long', price) and self.in_position == 1:
                self.in_position = False
                return 2
            if self.__evaluate_signal('exit_short', price) and self.in_position == 3:
                self.in_position = False
                return 4



"""
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
"""











