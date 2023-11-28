# Changelog

# 0.1.0a - 26 November 2023 #
- Initial release

# 0.1.1a - 27 November 2023 #
- Update documentation

# 0.2.0a - 27 November 2023 #
- Begin tick optimization
- Fix `CandleCluster.history()` method which broke code when calculating
- Major change to indicators and signals: They are no longer calculated
based on a chart's entire data, they are now calculated as you add each
to the chart. This makes calculating real-time indicator data and generating
the latest signals much faster.

# 0.2.1a -  27 November 2023 #

- Fixed bug in `Backtester` class that caused improper reading of signals and
resulted in improper trade entry and exit
- More tick optimizations