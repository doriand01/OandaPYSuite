from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.stats import candlex

from datetime import datetime, timedelta
from random import random
from time import sleep
from math import ceil
from decimal import Decimal
from copy import deepcopy

import asyncio
import abc


class Account:

    def __init__(self, details: dict):
        for key, value in details.items():
            setattr(self, key, value)
        print(f'Loaded account with id {self.id}')

    def __repr__(self):
        return f'Account {self.id}'


class Trade:

    def __init__(self, details: dict):
        for key, value in details.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'Trade {self.id}'


class MarketSimulator:

    def __update_price(self, candle, is_close=False, is_open=False):
        if is_close: self.current_price = candle.close
        elif is_open: self.current_price = candle.open
        else:
            if candle.open > candle.close:
                up_or_down = lambda: Decimal(1.2) if random() > .5 else -1
            else:
                up_or_down = lambda: 1 if random() > .5 else Decimal(-1.2)
            self.current_price += candle.low + up_or_down() *((candle.high-candle.low) * Decimal(ceil(random()*20)*5/200))
            if self.current_price > candle.high: self.current_price = candle.high
            elif self.current_price < candle.low: self.current_price = candle.low

    def __get_candle_at_time(self, candle, target_time):
        if candle.gran == self.generate_for:
            adjusted_candle = deepcopy(candle)
            adjusted_candle.close = self.current_price
            self.candles_dict[candle.time] = adjusted_candle
        if candle.has_lower_timeframe():
            lower_timeframe = candle.get_lower_timeframe()
            cache_key = (candle.gran, candle.time)
            if self.speed_factor/self.tps > candlex[lower_timeframe]/4:
                return candle
            if cache_key in self.candle_cache:
                children = self.candle_cache[cache_key]
            else:
                children = self.api.get_child_candles(candle, lower_timeframe)
                self.candle_cache[cache_key] = children
            for cand in reversed(children.candles):
                if target_time < cand.time:
                    continue

                # Cache the result
                if cand.has_lower_timeframe():
                    return self.__get_candle_at_time(cand, target_time)
                return cand

        if not candle.has_lower_timeframe():
            return candle

    def pause(self):
        print("Simulation paused                  ", end="\r")
        self.paused = True

    def play(self):
        self.paused = False

    def __init__(self, window, api_object, speed_factor=1.0, ticks_per_second=20, generate_for='S5'):
        self.window = window
        self.candles_dict = {}
        self.start_time = self.window[0].time
        self.current_time = self.window[0].time
        self.current_price = self.window[0].open
        self.api = api_object
        self.tps = ticks_per_second
        self.speed_factor = speed_factor
        self.candle_cache = {}  # Cache for storing fetched candle data
        self.generate_for = generate_for
        self.current_candle = self.__get_candle_at_time(window[0], self.current_time)
        self.current_tick = 0
        self.paused = False

    def get_candle_cluster(self):
        return CandleCluster(cand_list=list(self.candles_dict.values()))


    def run(self):
        for i in range(len(self.window)):
            current_macro_candle = self.window[i]
            while self.current_time < current_macro_candle.time + timedelta(seconds=candlex[current_macro_candle.gran]):
                if self.current_candle and self.current_time > self.current_candle.time + timedelta(
                        seconds=candlex[self.current_candle.gran]):
                    self.__update_price(self.current_candle, is_close=True)
                    self.current_candle = self.__get_candle_at_time(current_macro_candle, self.current_time)
                    self.__update_price(self.current_candle, is_open=True)
                self.__update_price(self.current_candle)
                print(f'{self.current_time} price:{self.current_price}', end="\r")
                self.current_time += timedelta(seconds=(self.speed_factor / self.tps))
                sleep_interval = 1 / self.tps
                sleep(sleep_interval)
                self.current_tick += 1

class Backtester(MarketSimulator):

    def __enter_trade(self, trade_type):
        self.trade_type = trade_type
        self.entry_price = self.current_price

    def __exit_trade(self):
        self.entry_price = 0
        self.trade_type = 0

    def __check_signal(self):
        cands = self.get_candle_cluster()
        altavd = self.indicators[1](cands, on='open', period=100, name='altav', color='green')
        sma = self.indicators[0](cands, on='open', period=200, name='sma', color='black')
        mvdiff = self.signal(cands, [altavd, sma])
        if self.trade_type == 0:
            if mvdiff.data.iloc[-1]['y'] == 1:
                print(f'Entering long @ {self.current_price}, time: {self.current_time}')
                self.__enter_trade(trade_type=1)
            if mvdiff.data.iloc[-1]['y'] == 2:
                print(f'Entering short @ {self.current_price}, time: {self.current_time}')
                self.__enter_trade(trade_type=2)
        if self.trade_type != 0:
            if self.trade_type == 1 and mvdiff.data.iloc[-1]['y'] == 3:
                self.__exit_trade()
                print(f'Exiting long, profit:{(self.current_price - self.entry_price) * 10000}  time: {self.current_time}')
                self.trades.append((self.current_price - self.entry_price) * 10000)
            if self.trade_type == 2 and mvdiff.data.iloc[-1]['y'] == 4:
                self.__exit_trade()
                print(f'Exiting long, profit:{(self.entry_price - self.current_price) * 10000}  time: {self.current_time}')
                self.trades.append((self.entry_price - self.current_price) * 10000)

    def __update_price(self, candle, is_close=False, is_open=False):
        if is_close: self.current_price = candle.close
        elif is_open: self.current_price = candle.open
        else:
            if candle.open > candle.close:
                up_or_down = lambda: Decimal(1.2) if random() > .5 else -1
            else:
                up_or_down = lambda: 1 if random() > .5 else Decimal(-1.2)
            self.current_price += candle.low + up_or_down() *((candle.high-candle.low) * Decimal(ceil(random()*20)*5/200))
            if self.current_price > candle.high: self.current_price = candle.high
            elif self.current_price < candle.low: self.current_price = candle.low
        if self.periods > 250:
            self.__check_signal()

    def __get_candle_at_time(self, candle, target_time):
        pass
        if candle.gran == self.generate_for:
            adjusted_candle = deepcopy(candle)
            adjusted_candle.close = self.current_price
            self.candles_dict[candle.time] = adjusted_candle
        if candle.has_lower_timeframe():
            lower_timeframe = candle.get_lower_timeframe()
            cache_key = (candle.gran, candle.time)
            if abs(self.speed_factor/self.tps) > candlex[lower_timeframe]/4:
                return candle
            if cache_key in self.candle_cache:
                children = self.candle_cache[cache_key]
            else:
                children = self.api.get_child_candles(candle, lower_timeframe)
                self.candle_cache[cache_key] = children
            for cand in reversed(children.candles):
                if target_time < cand.time:
                    continue

                # Cache the result
                if cand.has_lower_timeframe():
                    return self.__get_candle_at_time(cand, target_time)
        return candle

    def __init__(self, window, api_object, speed_factor=1.0, ticks_per_second=20, generate_for='M1', signal=None, indicators=None):
        super().__init__(window, api_object, speed_factor=speed_factor, ticks_per_second=ticks_per_second)
        self.signal = signal
        self.indicators = indicators
        self.generate_for = generate_for
        self.entry_price = 0
        self.trade_type = 0
        self.disp = 0
        self.trades = []
        self.periods = 0

    def run(self):
        for i in range(len(self.window)):
            current_macro_candle = self.window[i]
            while self.current_time < current_macro_candle.time + timedelta(seconds=candlex[current_macro_candle.gran]):
                if self.current_candle and self.current_time > self.current_candle.time + timedelta(
                        seconds=candlex[self.current_candle.gran]):
                    self.__update_price(self.current_candle, is_close=True)
                    self.current_candle = self.__get_candle_at_time(current_macro_candle, self.current_time)
                    self.__update_price(self.current_candle, is_open=True)
                    print(f'price:{self.current_price}, tickno.:{self.current_tick}, pds:{self.periods} time:{self.current_time}', end="\r")
                self.__update_price(self.current_candle)
                self.current_time += timedelta(seconds=(self.speed_factor / self.tps))
                sleep_interval = 1 / self.tps
                sleep(sleep_interval)
                self.current_tick += 1
                self.periods = len(list(self.candles_dict.values()))


# Assuming candlex is defined somewhere in your code




