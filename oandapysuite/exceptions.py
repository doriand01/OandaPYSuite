

class ArgumentError(Exception):

    def __init__(self, msg):
        super(ArgumentError, self).__init__(msg)

class TimedeltaMismatchException(Exception):

    def __init__(self):
        super(TimedeltaMismatchException, self).__init__('Granularity cannot be larger than the timedelta.')

class InvalidGranularityException(Exception):

    def __init__(self):
        super(InvalidGranularityException, self).__init__('Invalid granularity specified.')

class HighestGranularityException(Exception):

    def __init__(self):
        super(HighestGranularityException, self).__init__('Granularity cannot be higher.')

class LowestGranularityException(Exception):

    def __init__(self):
        super(LowestGranularityException, self).__init__('Granularity cannot be lower.')