# Bug Tracker

---

## Unpatched Bugs

### 001 ###
- oandapysuite.objects.trade.Backtester will freeze at 17:00 each Friday when the market closes. This is because the market closes at 17:00 on 
Fridays and the Backtester is waiting for the next candle to be added to the chart.
- Last known version affected: 0.3.4a

### 002 ###
- Using the API's `get_candles()` method to retrieve candles from a Unix timestamp that is over the weekend will result in a CandleCluster
object being returned Candles missing from the cluster. This is because the API returns candles only for the days the market is open.
- Last known version affected: 0.3.4a

### 003 ###
- Using the API's `get_child_candles()` method to retrieve children candles on a Candle that has not yet closed will result in a 
in an APIError with the following message "Invalid value specified for 'to'. The time is in the future".
- Last known version affected: 0.3.4a

---

## Patched Bugs

- Nothing here, yet :)