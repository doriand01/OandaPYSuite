

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

class ClusterConcatException(Exception):

    def __init__(self, ins1, ins2):
        super(ClusterConcatException, self).__init__(f'Cannot add clusters of two different instrumens: {ins1} + {ins2}')