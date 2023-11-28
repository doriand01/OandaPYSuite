# Changelog

---

# Pre-Alpha ##

## August 2021 ###

### 0.0.0pre-a rev2 ### 
- Implemented addition feature on CandlesObject class. Renamed CandlesObject to CandleCluster for clarity
- Added ability to plot horizontal and vertical lines to `OANDAAPIObject.plot()`. To do so, run `plot(x=x1, style='vline')`. For a vertical line. For a horizontal line, use `'hline'` instead of `'vline'` and `y` instead of `x`.

### 0.0.0pre-a rev3 ####
- Added documentation

#### October 2021 ####

### 0.0.1pre-a ###

- Implemented Account objects. Account objects have every attribute present in `Account` per the OANDA REST API's documentation.
- Reimplemented `api.APIObject`'s `get_accounts()` method, this method can now be used to retrieve the account objects
of every account owned by the given Authorization token.
- Implemented a standard deviation indicator function `stats.std_indicator`. Period can be specified as with the `moving_average()`, indicator, default period is 10.

---

# Alpha ##

## November 2023 ####

### 0.1.0a - 26 November 2023 ###
- Initial release

### 0.1.1a - 27 November 2023 ###
- Update documentation

### 0.2.0a ###
- Begin tick optimization
- Fix `CandleCluster.history()` method which broke code when calculating
- Major change to indicators and signals: They are no longer calculated
based on a chart's entire data, they are now calculated as you add each
to the chart. This makes calculating real-time indicator data and generating
the latest signals much faster.

### 0.2.1a  ###

- Fixed bug in `Backtester` class that caused improper reading of signals and
resulted in improper trade entry and exit
- More tick optimizations
- Deprecated `BaseSignal().sig_algorithm` in for `BaseSignal().get_signal()`.

### 0.2.2a - 28 November 2023 #

- Deprecated and removed `BaseIndicator().ind_algorithm()` function. Implement `add_candle()`
to add data to your indicators. Use `BaseIndicator.add_candle()` to populate your indicators 
with candle data from the market.
- Signals now accept a single candle (the most recent candle from the market) as an argument
rather than a whole candle cluster. You can also pass in your indicators pre-populated with data
to your signal class to get a signal.
- Clean up changelog and other files

### 0.2.3a ###
- Removed `AverageAverageDifference` indicator.
- Removed magic variables and magic constants from `Backtester` class.