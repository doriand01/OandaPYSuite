import oandapysuite.objects.signals
from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.objects.datatypes import candlex
from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite.objects.signals import BaseSignal

from multiprocessing.pool import ThreadPool
from datetime import datetime, timedelta
from random import random
from time import sleep
from math import ceil
from decimal import Decimal
from copy import deepcopy

import asyncio
import abc
import csv
import os


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
    """
    This object provides a live market simulation of historic market data.
    """

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

    # Uses recursive logic to get the relevant candle for a specified target time. The candle to be returned depends on
    # what the target time is, as well as the speed of the simulation. In order for the simulation to run properly,
    # there needs to be enough tick updates within a specified timeframe (at least four) for the market to correctly
    # simulate the historic price components for each candle (open, low, high, close). If the simulation is running too
    # fast, the tick updates will not be able to properly simulate the price components for each candle, and the
    # simulation will not be accurate. If the time delta (how far forward in time the simulation advances per tick)
    # is greater than 1/4 the length of the timeframe, then that timeframe is too low to be simulated, and the
    # candles from the higher timeframe will be returned instead. Otherwise, the candles from the lowest possible
    # timeframe that can be simulated under the simulation conditions will be returned.
    def __get_candle_at_time(self, candle, target_time):

        # If the granularity of the current candle is equal to the timeframe we want to generate a candle chart for,
        # (as specified in the `self.generate_for` attribute) then the current candle will be added to a dictionary which
        # represents the current state of the market.
        if candle.gran == self.generate_for:
            adjusted_candle = deepcopy(candle)
            adjusted_candle.close = self.current_price
            self.candles_dict[candle.time] = adjusted_candle

        # Sees if the candle has a lower timeframe.
        if candle.has_lower_timeframe():
            lower_timeframe = candle.get_lower_timeframe()
            cache_key = (candle.gran, candle.time)

            # If the change in time for each tick is greater than the lower timeframe divided by 4,
            # the current candle is returned. The returned candle's timeframe is the lowest that can be
            # accurately rendered by the simulations given the settings they were run with.
            if self.speed_factor/self.tps > candlex[lower_timeframe]/4:
                return candle

            # If the candle's child candles have been saved in cache already, they are retrieved from cache
            # in order to reduce the load on OANDA's API.
            if cache_key in self.candle_cache:
                children = self.candle_cache[cache_key]

            # If the child candles are not in the cache, they are retrieved using the `get_child_candles()`
            # method from the API. They are then stored in cache for future use.
            else:
                children = self.api.get_child_candles(candle, lower_timeframe)
                self.candle_cache[cache_key] = children

            # Iterates backwards over the child candles.
            for cand in reversed(children.candles):
                # If the open time of the candle is less than the target time, the child candle is too far
                # in the future and is not the current candle. The loop continues to the next one.
                if target_time < cand.time:
                    continue

                # If the child candle has a lower timeframe, this entire function is called again recursively,
                # except with the child candle.
                if cand.has_lower_timeframe():
                    return self.__get_candle_at_time(cand, target_time)

        # If a candle has not been returned yet, and the candle is of the lowest possible timeframe,
        # (typically the S5 timeframe) then the candle is returned, representing the end of the recursion.
        return candle

    def pause(self):
        print("Simulation paused                  ", end="\r")
        self.paused = True

    def play(self):
        self.paused = False

    def __init__(
            self,
            window,
            api_object,
            speed_factor=1.0,
            ticks_per_second=20,
            signal: BaseSignal = None):
        """
        Creates the MarketSimulator.

        __init__(
            self,
            window: CandleCluster() <-- window is the range of historic data you want to simulate market data for.
            api_object: API() <-- An instantiated API object.
            speed_factor: float <-- How fast the simulation runs. A speed factor of 2 will run 2x faster than real time.
            ticks_per_second: int <-- How often the simulation updates.
            generate_for: str <-- The timeframe that the simulation is running on. 'M1' will generate an M1 candlestick chart.
        )

        """
        self.window = window
        self.current_candle_index = 0
        self.candles_dict = {}
        self.start_time = self.window[0].time
        self.current_time = self.window[0].time
        self.current_price = self.window[0].open
        self.api = api_object
        self.tps = ticks_per_second
        self.speed_factor = speed_factor
        self.candle_cache = {}  # Cache for storing fetched candle data
        self.current_tick = 0
        self.periods = 0
        self.signal = signal
        self.candle_retriever_thread = ThreadPool(processes=1)
        self.paused = False

    def get_candle_cluster(self):
        """
        Returns the CandleCluster object for the simulated market. Takes no arguments.
        """
        return CandleCluster(cand_list=list(self.candles_dict.values()))

    def _market_is_open(self):
        weekday = self.current_time.weekday()
        hour = self.current_time.hour
        if weekday >= 4:
            if weekday == 6 and hour >= 17:
                return True
            elif weekday == 4 and hour <= 17:
                return True
            return False
        return True



    def _do_tick(self):
        # If the current time is greater than the current candle's closing (meaning that the current candle has closed)
        # the next candle is fetched using the __get_candle_at_time() method.
        next_candle_time = self.window[self.current_candle_index + 1].time
        if self.current_time > next_candle_time:
            self.__update_price(self.current_candle, is_close=True)
            self.current_candle_index += 1
            self.periods += 1
            self.current_candle = self.window[self.current_candle_index]
            self.__update_price(self.current_candle, is_open=True)
            print(
                f'price:{self.current_price}, tickno.:{self.current_tick}, pds:{self.periods} time:{self.current_time}',
                end="\r")
        self.__update_price(self.current_candle)
        if self._market_is_open():
            self.current_time += timedelta(seconds=(self.speed_factor / self.tps))
        else:
            self.current_time += timedelta(days=2)
        sleep_interval = 1 / self.tps
        sleep(sleep_interval)
        self.current_tick += 1


    def run(self):
        """
        Begins the simulation. Takes no arguments.
        """

        # This loop iterates over every candle in the provided historic data. The topmost level candle is called the
        # `macro candle`.
        try:
            while True:
                self._do_tick()
        except KeyboardInterrupt:
            print(f'Exiting simulation at {self.current_time}')


class Backtester(MarketSimulator):

    def __enter_trade(self, trade_type):
        self.trade_type = trade_type
        self.entry_price = self.current_price
        self.entry_time = self.current_time
        self.equity_curve.append(self.equity_curve[-1])  # Append the current equity for drawdown calculation

    def __exit_trade(self):
        self.entry_price = 0
        self.trade_type = 0

    def __log_trade(self, exit_price, profit, movement_in_pips):
        trade_details = {
            'time_opened': self.entry_time,
            'time_closed': self.current_time,
            'entry_price': self.entry_price,
            'exit_price': exit_price,
            'movement_in_pips': movement_in_pips,
            'profit_in_pips': profit
        }
        self.trade_log.append(trade_details)

    def __check_signal(self):
        candle_cluster = CandleCluster(cand_list=list(self.window.candles.iloc[:self.current_candle_index+1])) # Add one to include the current candle
        sig_val = self.signal.get_signal(self.current_candle, cluster=candle_cluster)
        if self.trade_type == 0:
            if sig_val == 1:
                print(f'''Entering long @ {self.current_price}, time: {self.current_time} '''
                      f'''TP:{self.signal.take_profit}, SL:{self.signal.stop_loss}''')
                self.__enter_trade(trade_type=1)
            elif sig_val == 3:
                print(f'''Entering short @ {self.current_price}, time: {self.current_time},''' 
                f'''TP:{self.signal.take_profit}, SL:{self.signal.stop_loss}''')
                self.__enter_trade(trade_type=3)
        else:
            if self.trade_type == 1 and sig_val == 2:
                profit = (self.current_price - self.entry_price) * 10000
                movement_in_pips = (self.current_price - self.entry_price) * 10000
                print(f'''Exiting long, price:{self.current_price}  time: {self.current_time}, profit:{profit}''')
                self.trades.append(profit)
                self.equity_curve.append(self.equity_curve[-1] + profit)
                self.__log_trade(self.current_price, profit, movement_in_pips)
                self.__exit_trade()
            elif self.trade_type == 3 and sig_val == 4:
                profit = (self.entry_price - self.current_price) * 10000
                movement_in_pips = (self.entry_price - self.current_price) * 10000
                print(f'''Exiting short, price:{self.current_price}  time: {self.current_time}, profit:{profit}''')
                self.trades.append(profit)
                self.equity_curve.append(self.equity_curve[-1] + profit)
                self.__log_trade(self.current_price, profit, movement_in_pips)
                self.__exit_trade()

    def __update_price(self, candle, is_close=False, is_open=False):
        if is_close:
            self.current_price = candle.close
        elif is_open:
            self.current_price = candle.open
        else:
            up_or_down = [lambda: 1 if random() > .5 else Decimal(-1.2), lambda: Decimal(1.2) if random() > .5 else -1][candle.open > candle.close]
            self.current_price += up_or_down() * ((candle.high - candle.low) * Decimal(ceil(random() * 20) * 5 / 200))
            if self.current_price > candle.high:
                self.current_price = candle.high
            elif self.current_price < candle.low:
                self.current_price = candle.low

    def __get_candle_at_time(self, candle, target_time):
        if candle.gran == self.generate_for:
            adjusted_candle = deepcopy(candle)
            adjusted_candle.close = self.current_price
            self.candles_dict[candle.time] = adjusted_candle
        if candle.has_lower_timeframe():
            lower_timeframe = candle.get_lower_timeframe()
            cache_key = (candle.gran, candle.time)
            if abs(self.speed_factor / self.tps) > candlex[lower_timeframe] / 4:
                return candle
            if cache_key in self.candle_cache:
                children = self.candle_cache[cache_key]
            else:
                children = self.api.get_child_candles(candle, lower_timeframe)
                self.candle_cache[cache_key] = children
            for cand in reversed(children.candles):
                if target_time < cand.time:
                    continue
                if cand.has_lower_timeframe():
                    return self.__get_candle_at_time(cand, target_time)
        return candle

    def __init__(self, window, api_object, speed_factor: float = 1.0, ticks_per_second: int = 20, generate_for: str = 'M1', signal: BaseSignal = None):
        super().__init__(window, api_object, speed_factor=speed_factor, ticks_per_second=ticks_per_second, signal=signal)
        self.current_candle = self.window[0]
        self.signal = signal
        self.generate_for = generate_for
        self.entry_price = 0
        self.entry_time = None
        self.trade_type = 0
        self.trades = []
        self.equity_curve = [10000]  # Starting equity
        self.trade_log = []  # List to store trade details

    def _do_tick(self):
        super()._do_tick()
        if self.periods > self.signal.max_period:
            self.__check_signal()

    def run(self):
        try:
            while True:
                    self._do_tick()
                    print(f'price:{self.current_price}, tickno.:{self.current_tick}, pds:{self.periods} time:{self.current_time}', end="\r", flush=True)
        except KeyboardInterrupt:
            print(f'Exiting simulation at {self.current_time}')
            self._calculate_statistics()
            self._output_trade_log()

    def _calculate_statistics(self):
        drawdowns = []
        peak = self.equity_curve[0]
        max_drawdown = 0
        max_drawdown_duration = 0
        drawdown_duration = 0

        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
                if drawdown_duration > 0:
                    drawdowns.append(drawdown_duration)
                drawdown_duration = 0
            else:
                drawdown_duration += 1
                drawdown = (peak - equity) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                drawdowns.append(Decimal(drawdown))

        avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else 0
        max_drawdown_percentage = max_drawdown * 100
        avg_drawdown_percentage = avg_drawdown * 100
        avg_drawdown_period = sum(drawdowns) / len(drawdowns) if drawdowns else 0
        max_drawdown_period = max(drawdowns) if drawdowns else 0

        wins = [trade for trade in self.trades if trade > 0]
        losses = [trade for trade in self.trades if trade < 0]
        win_ratio = len(wins) / len(self.trades) if self.trades else 0
        max_win = max(wins) if wins else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        max_win_percentage = (max_win / self.equity_curve[0]) * 100
        avg_win_percentage = (avg_win / self.equity_curve[0]) * 100

        print(f'Average Drawdown Percentage: {avg_drawdown_percentage:.2f}%')
        print(f'Max Drawdown Percentage: {max_drawdown_percentage:.2f}%')
        print(f'Average Drawdown Period: {avg_drawdown_period}')
        print(f'Max Drawdown Period: {max_drawdown_period}')
        print(f'Equity Curve: {self.equity_curve}')
        print(f'Win Ratio: {win_ratio:.2f}')
        print(f'Max Win Percentage: {max_win_percentage:.2f}%')
        print(f'Average Win Percentage: {avg_win_percentage:.2f}%')

    def _output_trade_log(self):
        log_file = 'trade_log.csv'
        with open(log_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['time_opened', 'time_closed', 'entry_price', 'exit_price', 'movement_in_pips', 'profit_in_pips'])
            writer.writeheader()
            for trade in self.trade_log:
                writer.writerow(trade)
        print(f'Trade log saved to {log_file}')