# Bug Tracker and Todos

---
## Todos

### In progress

- **040-001-008** Deprecate stats.py and refactor references to it. (Priority: low)




### Done
- **035-001-001** Refactor `add_candle()` method of `BaseIndicator` classes to `update()` (Done in 0.3.5a)
- **035-005-005** Patch bug 002. (Done in 0.4.0a)
- **035-004-004** Patch bug 001. (Done in 0.4.0a)

### Planned


### Abandoned
- **035-002-002** Refactor BaseIndicator() to take a `CandleCluster` object when instantiated. 
- **035-003-003** Refactor test cases to reflect 035-001-001 and 035-002-002.
- **035-006-006** Patch bug 003. Will get to this later (Abandoned in 0.4.0a)
- **035-007-007** Patch bug 004. Will get to this later (Abandoned in 0.4.0a)

## Unpatched Bugs

### 003 ###
- Using the API's `get_child_candles()` method to retrieve children candles on a Candle that has not yet closed will result in a 
in an APIError with the following message "Invalid value specified for 'to'. The time is in the future".
- Last known version affected: 0.3.5a

### 004 ###
- There's a discrepancy between requested datetimes and return datetimes with the UnixTime object. 
this is most likely due to timezone offset between local time and UTC time.
- Last known version affected: 0.3.5a

### 005 ###
- DST change in March and November each year breaks datetime representation for candles. This is because the API returns candles
based on UTC time, and the UnixTime object converts the local time to UTC. Major bug with cascading effects. on every
function that relies on the UnixTime object, as well as time calculations and precision.
- Last known version affected: 0.3.5a

---

## Patched Bugs

### 002 ###
- Using the API's `get_candles()` method to retrieve candles from a Unix timestamp that is over the weekend will result in a CandleCluster
object being returned Candles missing from the cluster. This is because the API returns candles only for the days the market is open.
- Last known version affected: 0.3.5a
- Patched in: 0.4.0a
- Patch: None. This is not a bug. This is the intended behavior of the API. The API returns candles only for the days the market is open. 
it is up to methods to rely on get_candles() to properly handle this behavior. Possible other solutions include error handling
for when the API returns an empty list

### 001 ###
- oandapysuite.objects.trade.Backtester will freeze at 17:00 each Friday when the market closes. This is because the market closes at 17:00 on 
Fridays and the Backtester is waiting for the next candle to be added to the chart.
- Last known version affected: 0.3.5a
- Patched in: 0.4.0a
- Patch: Add _market_is_open() boolean method to check if the market is open. If the
market is open, then the timedelta to the next tick will be calculated as normal. If
the market is closed, the timedelta to the next tick will be two days.