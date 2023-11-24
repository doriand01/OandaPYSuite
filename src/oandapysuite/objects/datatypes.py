import datetime
from regex import finditer
from random import randint

from oandapysuite import settings

class UnixTime:

    # The __init__ function for the UnixTime object does a few things. The first is that it creates all of
    # the instance variables that it needs. The relevant ones are 'self.string_repr', which is a simple string
    # representation of the datetime provided by the user. `self.today` is simply a datetime object of the current
    # day's date using the datetime.date.today() function.
    # `time_string_unix_regex_iterator` uses the `finditer` function of the `regex` library to create an iterable that has
    # the matches for valid date-time formats for this object, as defined by settings.DATETIME_REGEX. Valid formats include
    # %H:%M or %H:%M:%S (without providing a date, will reference that hour on the today's date.)
    # %Y-%m-%d (without providing a time, will reference 00:00 on that date.)
    # %Y-%m-%d %H:%M or %H:%M:%S (Provide an exact date or time.)
    # The purpose of the different formats of time provided in this library is to make it easy to fetch candle data at
    # certain UNIX times without having to manually calculate the UNIX epoch for the given datetime that you want to
    # retrieve data.
    def __init__(self, time_string: str):
        if  type(time_string) == int or time_string.isdigit():
            self.string_repr = str(time_string)
            self.datetime_repr = datetime.datetime.fromtimestamp(int(time_string))
            self.timestamp = self.datetime_repr.timestamp()
            self.today = datetime.date.today()
            return
        self.string_repr = time_string
        self.today = datetime.date.today()
        time_string_unix_regex_iterator = finditer(settings.DATETIME_REGEX, time_string)
        time_string_parsed_groups = [match.group() for match in time_string_unix_regex_iterator]
        # If the length of the above generated list parsed groups from the regex is 1, then it is either
        # A specific date or a specific time.
        if time_string.lower() == 'now':
            self.datetime_repr = datetime.datetime.now()
            self.timestamp = int(self.datetime_repr.timestamp())
        if len(time_string_parsed_groups) == 1:

            time_string = time_string_parsed_groups[0]
            # If the string contains the colon ':' in the third position, it must be a specific time, since
            # The colon is required to denote a separate hour from a separate minute.
            if time_string[2] == ':':
                time_string = time_string.replace(' ', '-')
                self.datetime_repr = datetime.datetime.strptime(f'{str(self.today)} {time_string}', '%Y-%m-%d %H:%M')
            # If the string does not contain the colon in the third position, then it must be a specific date without
            # a specific time provided.
            else:
                self.datetime_repr = datetime.datetime.strptime(f'{time_string}', '%Y-%m-%d')
# If the length of the generated list `time_string_parsed_groups` is 2, then it contains both a specific date
        # AND a specific time, and a datetime object (stored in self.datetime_repr) with this date and time are created.
        elif len(time_string_parsed_groups) == 2:
            date = time_string_parsed_groups[0].replace(' ', '-')
            time = time_string_parsed_groups[1]
            self.datetime_repr = datetime.datetime.strptime(f'{date} {time}','%Y-%m-%d %H:%M')

        self.timestamp = int(self.datetime_repr.timestamp())

    def __repr__(self):
        return f"UnixTime Object: {self.datetime_repr.strftime('%Y-%m-%d %H:%M')}"

    @staticmethod
    def randomtime(start: str, end: str):
        rangestart = UnixTime(start).timestamp
        rangeend = UnixTime(end).timestamp
        randomtime = UnixTime(
            datetime.datetime.fromtimestamp(
                randint(rangestart, rangeend)
            ).strftime('%Y-%m-%d %H:%M')
        )
        return randomtime



# Granularity class provides string constants for all granularities available on the market, ranging from M1 to M.
class Granularity:
    m1 = 'M1'
    m2 = 'M2'
    m4 = 'M4'
    m5 = 'M5'
    m15 = 'M15'
    m30 = 'M30'
    h1 = 'H1'
    h2 = 'H2'
    h4 = 'H4'
    h6 = 'H6'
    h8 = 'H8'
    h12 = 'H12'
    d = 'D'
    w = 'W'
    m = 'M'