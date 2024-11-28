import oandapysuite.objects.signals
from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.objects.datatypes import candlex
from oandapysuite.objects.indicators import BaseIndicator
from oandapysuite.objects.signals import BaseSignal

from multiprocessing.pool import ThreadPool
from datetime import datetime, timedelta
from random import random
from time import time
from math import ceil
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
        """
        Updates the current price based on the candle's properties.
        Args:
            candle: An object representing the current candle with attributes (open, close, high, low).
            is_close (bool): If True, update the price to the close value.
            is_open (bool): If True, update the price to the open value.
        """
        open = candle[0]
        high = candle[1]
        low = candle[2]
        close = candle[3]


        if is_close:
            self.current_price = close
        elif is_open:
            self.current_price = open
        else:
            # Determine movement direction: higher weight towards up or down based on candle trend
            direction = 1.2 if random() > 0.5 else -1.2
            if open > close:
                direction = -direction  # Reverse direction for downward candles

            # Calculate the adjustment factor
            adjustment = direction * (high - low) * (random() * 0.5)

            # Update current price and enforce boundaries
            self.current_price = max(min(low + adjustment, high), low)

    # Uses recursive logic to get the relevant candle for a specified target time. The candle to be returned depends on
    # what the target time is, as well as the speed of the simulation. In order for the simulation to run properly,
    # there needs to be enough tick updates within a specified timeframe (at least four) for the market to correctly
    # simulate the historic price components for each candle (open, low, high, close). If the simulation is running too
    # fast, the tick updates will not be able to properly simulate the price components for each candle, and the
    # simulation will not be accurate. If the time delta (how far forward in time the simulation advances per tick)
    # is greater than 1/4 the length of the timeframe, then that timeframe is too low to be simulated, and the
    # candles from the higher timeframe will be returned instead. Otherwise, the candles from the lowest possible
    # timeframe that can be simulated under the simulation conditions will be returned.

    def __init__(
            self,
            window,
            api_object,
            speed_factor=1.0,
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
        self.start_time = self.window[0][4]
        self.current_time = self.window[0][4]
        self.current_price = self.window[0][0]
        self.api = api_object
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
        next_candle_time = self.window[self.current_candle_index + 1][4]
        if self.current_time > next_candle_time:
            self.__update_price(self.current_candle, is_close=True)
            self.current_candle_index += 1
            self.periods += 1
            self.current_candle = self.window[self.current_candle_index]
            self.__update_price(self.current_candle, is_open=True)
            return
        self.__update_price(self.current_candle)
        if self._market_is_open():
            self.current_time += timedelta(seconds=self.speed_factor)
        else:
            self.current_time += timedelta(days=2)
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
        lookback_start = self.current_candle_index - (self.signal.max_period * 4) if self.current_candle_index - (self.signal.max_period * 4) >= 0 else 0
        candles = self.window[lookback_start:self.current_candle_index+1] # Add one to include the current candle
        sig_val = self.signal.get_signal(self.current_price, cluster=candles)
        if self.trade_type == 0:
            if sig_val == 1:
                self.__enter_trade(trade_type=1)
            elif sig_val == 3:
                self.__enter_trade(trade_type=3)
        else:
            if self.trade_type == 1 and sig_val == 2:
                profit = ((0.0001/self.current_price) * 1000) * (((self.current_price - self.entry_price) * 10000) - 1)
                movement_in_pips = ((self.current_price - self.entry_price) * 10000)
                self.trades.append(profit)
                self.equity_curve.append(self.equity_curve[-1] + profit)
                self.__log_trade(self.current_price, profit, movement_in_pips)
                self.__exit_trade()
            elif self.trade_type == 3 and sig_val == 4:
                profit = ((0.0001/self.current_price) * 1000) * (((self.entry_price - self.current_price) * 10000) + 1)
                movement_in_pips = ((self.entry_price - self.current_price) * 10000)
                self.trades.append(profit)
                self.equity_curve.append(self.equity_curve[-1] + profit)
                self.__log_trade(self.current_price, profit, movement_in_pips)
                self.__exit_trade()

    def __update_price(self, candle, is_close=False, is_open=False):
        """
        Updates the current price based on the candle's properties.
        Args:
            candle: An object representing the current candle with attributes (open, close, high, low).
            is_close (bool): If True, update the price to the close value.
            is_open (bool): If True, update the price to the open value.
        """
        if is_close:
            self.current_price = candle.close
        elif is_open:
            self.current_price = candle.open
        else:
            # Determine movement direction: higher weight towards up or down based on candle trend
            direction = 1.2 if random() > 0.5 else -1.2
            if candle.open > candle.close:
                direction = -direction  # Reverse direction for downward candles

            # Calculate the adjustment factor
            adjustment = direction * (candle.high - candle.low) * (random() * 0.5)

            # Update current price and enforce boundaries
            self.current_price = max(min(candle.low + adjustment, candle.high), candle.low)

    def __init__(self, window, api_object, speed_factor: float = 1.0, generate_for: str = 'M1', signal: BaseSignal = None):
        super().__init__(window, api_object, speed_factor=speed_factor, signal=signal)
        self.current_candle = self.window[0]
        self.signal = signal
        self.generate_for = generate_for
        self.entry_price = 0
        self.entry_time = None
        self.trade_type = 0
        self.trades = []
        self.equity_curve = [200]  # Starting equity
        self.trade_log = []  # List to store trade details

    def _do_tick(self):
        super()._do_tick()
        if self.periods > self.signal.max_period:
            self.__check_signal()

    def run(self):
        try:
            print(f'Starting simulation at {self.current_time}')
            start_stamp = time()
            while True:
                self._do_tick()
        except (KeyboardInterrupt, IndexError):
            print(f'Exiting simulation at {self.current_time}')
            print(f'Simulation took {(time() - start_stamp) / 60:.2f} minutes to complete.')
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
                drawdowns.append(float(drawdown))

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

        print(f'End Time: {self.current_time}')
        print(f'Average Drawdown Percentage: {avg_drawdown_percentage:.2f}%')
        print(f'Max Drawdown Percentage: {max_drawdown_percentage:.2f}%')
        print(f'Average Drawdown Period: {avg_drawdown_period}')
        print(f'Max Drawdown Period: {max_drawdown_period}')
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