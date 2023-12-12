# Bug Tracker and Todos

---
## Todos

### In progress
- **035-004-004** Patch bug 001.
- **035-005-005** Patch bug 002.
- **035-006-006** Patch bug 003.
- **035-007-007** Patch bug 004.

### Done
- **035-001-001** Refactor `add_candle()` method of `BaseIndicator` classes to `update()`

### Planned


### Abandoned
- **035-002-002** Refactor BaseIndicator() to take a `CandleCluster` object when instantiated. 
- **035-003-003** Refactor test cases to reflect 035-001-001 and 035-002-002. 

## Unpatched Bugs

### 001 ###
- oandapysuite.objects.trade.Backtester will freeze at 17:00 each Friday when the market closes. This is because the market closes at 17:00 on 
Fridays and the Backtester is waiting for the next candle to be added to the chart.
- Last known version affected: 0.3.5a

### 002 ###
- Using the API's `get_candles()` method to retrieve candles from a Unix timestamp that is over the weekend will result in a CandleCluster
object being returned Candles missing from the cluster. This is because the API returns candles only for the days the market is open.
- Last known version affected: 0.3.5a

### 003 ###
- Using the API's `get_child_candles()` method to retrieve children candles on a Candle that has not yet closed will result in a 
in an APIError with the following message "Invalid value specified for 'to'. The time is in the future".
- Last known version affected: 0.3.5a

### 004 ###
- There's a discrepancy between requested datetimes and return datetimes with the UnixTime object. 
this is most likely due to timezone offset between local time and UTC time.
- Last known version affected: 0.3.5a

---

## Patched Bugs

- Nothing here, yet :)