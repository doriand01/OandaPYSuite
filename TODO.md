# Bug Tracker and Todos

---
## Todos

### In progress

- **040-001-008** Deprecate stats.py and refactor references to it. (Priority: low)
- **042-001-013** Add all ta indicators to the API. (Priority: high)


### Done
- **035-001-001** Refactor `add_candle()` method of `BaseIndicator` classes to `update()` (Done in 0.3.5a)
- **035-005-005** Patch bug 002. (Done in 0.4.0a)
- **035-004-004** Patch bug 001. (Done in 0.4.0a)
- **041-002-010** Clean up render_chart() method in API (Done in 0.4.1a)
- **041-003-011** Refactor initialize_chart() method in API to provide for custom options
when initializing candlestick charts. (Done in 0.4.1a)
- **042-002-014** Make indicators.py a package instead of a module. (Done in 0.4.2a)
- **043-001-015** Remove indicators.py (Done in 0.4.3a)
- **043-002-016** Remove candles column from indicator DataFrames. (Done in 0.4.3a)

### Planned


### Abandoned
- **035-002-002** Refactor BaseIndicator() to take a `CandleCluster` object when instantiated. 
- **035-003-003** Refactor test cases to reflect 035-001-001 and 035-002-002.
- **035-006-006** Patch bug 003. Will get to this later (Abandoned in 0.4.0a)
- **035-007-007** Patch bug 004. Will get to this later (Abandoned in 0.4.0a)
- **041-001-009** Clean up add_indicator() method in API. Couldn't figure out how lol. I'll probably do it later.
(Abandoned in 0.4.1a)

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