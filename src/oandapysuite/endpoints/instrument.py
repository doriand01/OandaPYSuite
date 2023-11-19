from oandapysuite.objects.datatypes import UnixTime
from oandapysuite.settings import REQUEST_PREFIX
from oandapysuite import exceptions
class Instrument:
    @staticmethod
    def get_candles(
                    ins: str,
                    granularity: str,
                    count: int=None,
                    from_time: UnixTime=None,
                    to_time: UnixTime=None,
                    include_first: bool=True
                    ) -> str:
        if count:
            return f'{REQUEST_PREFIX}/instruments/{ins}/candles?granularity={granularity}&count={count}'
        elif not count and from_time and to_time:
            return f'{REQUEST_PREFIX}/instruments/{ins}/candles?granularity={granularity}&from={from_time.timestamp}&to={to_time.timestamp}'
        else:
            raise exceptions.TimerangeValueException
