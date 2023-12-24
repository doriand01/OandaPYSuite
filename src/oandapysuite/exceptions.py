
class AccountsNotLoadedError(Exception):

    def __init__(self, msg):
        super(AccountsNotLoadedError, self).__init__("No accounts have been loaded in the API object. Load first them with load_accounts()")

class NoAccountSelectedError(Exception):

    def __init__(self, msg):
        super(NoAccountSelectedError, self).__init__("No accounts have been selected for use. Select an account from your available accounts to make a transaction.")
class ArgumentError(Exception):

    def __init__(self, msg):
        super(ArgumentError, self).__init__(msg)

class TimerangeValueException(Exception):
    def __init__(self, msg):
        super(TimerangeValueException, self).__init__(msg)


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

class IndicatorOptionsError(Exception):

    def __init__(self, msg):
        super(IndicatorOptionsError, self).__init__(f'{msg}')

class APIError(Exception):

    def __init__(self, code, msg):
        super(APIError, self).__init__(f'Request to API failed with code {code}:\n{msg}')

class SignalOptionsError(Exception):

    def __init__(self, msg):
        super(SignalOptionsError, self).__init__(f'{msg}')