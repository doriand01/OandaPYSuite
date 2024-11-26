# Changelog

---
# Alpha ##

## November 2024 ##

### 0.6.0a - 26 November 2024 ###

- Added `SignalFromXML` class to `signals` module. This class allows you to create signals from XML files.

## January 2024 ##

### 0.5.2a - 5 January 2024 ###


### 0.5.1a - 3 January 2024 ###
- Implemented parallel processing for calls to the __get_candle_at_time() method in the MarketSimulator class. This should considerably
speed up execution of the market simulation. (TD-50.1.28)

### 0.5.0a ###
- Added default colors to indicators. For indicators that are just lines, the default is randomly generated.
For indicators that have multiple traces (such as MACD), the default colors are blue and red and green.

## December 2023 ##

### 0.4.7a - 29 December 2023 ###
- Deprecated chart rendering functionality in API class since it was moved to RenderEngine class. (TD-47.1.27)
- Added histogram plotting functionality to the RenderEngine, allowing MACD and other indicators to be plotted.

### 0.4.6a - 27 December 2023 ###
- Add render.py module to handle rendering charts and add RenderEngine class. Finishes TD-46.1.25

### 0.4.5a - 25 December 2023 ###
- Finish TD-40.1.8: deprecated stats.py and refactor references to it.
- Finish TD-43.6.20: Add functionality in get_candles() _from and to parameters to accept integers as arguments.
- Refactored _from and to parameters and renamed them to start and end.
- Added previously unimplemented indicators from TA-lib: KAMA, StochasticRSI, UltimateOscillator, DPO,
- Add signal and histogram to PercentagePriceOscillator indicator.
- test_indicators test case now fails. Need to fix this.

### 0.4.4a - 24 December 2023 ###
- Add ta-lib's EMA indicator.
- Finished TD-43.3.17: Clean up BaseSignal class and how the indicators are used.

### 0.4.3a - 12 December 2023 ###
- Add several indicators to from ta-lib to indicators module. There are some left that have been added soon that 
need to be added. See TODO.md for more details. TA indicators that require advanced chart renderings (histograms, signal)
line etc. will be added in a future release.
- Remove data['candles'] column from indicators. This column is no longer needed.
- Remove related test coverage for data['candles'] column.

### 0.4.2a ###
- Refactored indicators.py from a module to a package.
- Added KeltnerChannel, AverageTrueRange, DonchianChannel, and UlcerIndex indicators, in accordance with
TD-42.1.13

### 0.4.1a ###
- Reimplemented BollingerBands indicator. First indicator to use pandas ta library. Will begin
refactoring other indicators to use pandas ta library in future releases.
- TD-41.2.10: Refactored render_chart(), removed old `live` functionality.
- TD-41.3.11: Added options for OHLC or Candlestick chart when initializing chart.

### 0.4.0a ###
- TD-35.4.4: Fixed bug in Backtester/MarketSimulator where the market would freeze at 17:00 on Fridays.
due to the market closing.

### 0.3.5a ###
- Add more test coverage.
- Finished TD-35.1.1: Refactor `add_candle()` method of `BaseIndicator` classes to `update()`

### 0.3.4a ###
- Add test coverage for the following methods: API(), API().load_accounts, 
API().select_account oandapysuite.api.API.get_candles(), oandapysuite.api.API.get_child_candles()
- Add bug tracker and todo list
- Remove unused code/magic modules. Will reimplement some of them as tests in the future.

### 0.3.3a - 11 December 2023 ###
- Remove unused code in oandapysuite.stats module. Might deprecate this module in the future.
- Refactored SimpleMovingAverage, SampleStandardDeviation, ZScoreOfPrice, and AverageDifference indicators
to utilize pandas Series.rolling calculations. This makes calculating indicators much faster. Will refactor
other indicators in the future.

### 0.3.2a - 8 December 2023 ###
- Begin moving away from Python's lists and dict structures in favor of 
Pandas DataFrames. Change `self.candles` in `CandleCluster` to from a list to a Series.

### 0.3.1a - 2 December 2023 ###
- Temporary bug fix in Backtester and CandleCluster classes where DST offset changing
during the year breaks the `api.get_candles()` and `get_child_candles()` functions. Every
function that uses/relies on these methods is affected by this bug.

## November 2023 ####

### 0.3.0a - 30 November 2023 ###
- Begin optimizing indicators. Indicators are now calculated as you add candles to the chart.
- Added Bollinger Bands, ZScoreOfPrice, SampleStandardDeviation, DifferenceBetween and indicators.
- Need to remove magic function from api.add_indicator() that was coded specifically
for the BollingerBands. Find better way to accomodate graphing multiple y values on the same
x axis.

### 0.2.4a - 29 November 2023 ###
- Tidying up, removing unused code, and fixing bugs. MarketSimulator is about
as optimized as it can get for now. May probably be optimized further in the future.

### 0.2.3a #
- Deprecated and removed `BaseIndicator().ind_algorithm()` function. Implement `add_candle()`
to add data to your indicators. Use `BaseIndicator.add_candle()` to populate your indicators 
with candle data from the market.
- Signals now accept a single candle (the most recent candle from the market) as an argument
rather than a whole candle cluster. You can also pass in your indicators pre-populated with data
to your signal class to get a signal.
- Clean up changelog and other files

### 0.2.2a #

- Deprecated and removed `BaseIndicator().ind_algorithm()` function. Implement `add_candle()`
to add data to your indicators. Use `BaseIndicator.add_candle()` to populate your indicators 
with candle data from the market.
- Signals now accept a single candle (the most recent candle from the market) as an argument
rather than a whole candle cluster. You can also pass in your indicators pre-populated with data
to your signal class to get a signal.
- Clean up changelog and other files

### 0.2.1a - 27 November 2023 ###

- Fixed bug in `Backtester` class that caused improper reading of signals and
resulted in improper trade entry and exit
- More tick optimizations
- Deprecated `BaseSignal().sig_algorithm` in for `BaseSignal().get_signal()`.

### 0.2.0a ###
- Begin tick optimization
- Fix `CandleCluster.history()` method which broke code when calculating
- Major change to indicators and signals: They are no longer calculated
based on a chart's entire data, they are now calculated as you add each
to the chart. This makes calculating real-time indicator data and generating
the latest signals much faster.

### 0.1.1a ###
- Update documentation

### 0.1.0a - 26 November 2023 ###
- Initial release

---

# Pre-Alpha ##


#### October 2021 ####

### 0.0.1pre-a ###

- Implemented Account objects. Account objects have every attribute present in `Account` per the OANDA REST API's documentation.
- Reimplemented `api.APIObject`'s `get_accounts()` method, this method can now be used to retrieve the account objects
of every account owned by the given Authorization token.
- Implemented a standard deviation indicator function `stats.std_indicator`. Period can be specified as with the 
`moving_average()`, indicator, default period is 10.

### 0.0.0pre-a rev3 ####
- Added documentation

## August 2021 ###

### 0.0.0pre-a rev2 ### 
- Implemented addition feature on CandlesObject class. Renamed CandlesObject to CandleCluster for clarity
- Added ability to plot horizontal and vertical lines to `OANDAAPIObject.plot()`. To do so, run `plot(x=x1, style='vline')`.
For a vertical line. For a horizontal line, use `'hline'` instead of `'vline'` and `y` instead of `x`.
