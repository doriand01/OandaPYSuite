from pandas import DataFrame
from oandapysuite.objects.instrument import CandleCluster
from oandapysuite.exceptions import IndicatorOptionsError

import math
import decimal

D = decimal.Decimal

decimal.getcontext().prec = 6

class BaseIndicator:
    """
    BaseIndicator is the class that all other indicators inherit from. It allows functions to be defined
    that take CandleCluster objects as paramaters to create a data point for the specified time range of
    candles. These can indicators can then be added to the chart and rendered using the API.
    To create a custom indicator, your indicator class must inherit from the BaseIndicator class, and it must
    override the `BaseIndicator.ind_algorithm() function. This function takes one parameter (besides self) as
    an argument, which is the CandleCluster object. Here in this function, you can run your statistics over
    the data to calculate the values for your indicators, however, the ind_algorithm function must return a pandas
    dataframe with at least two columns, one for the x-axis (time) for each data point, and the others with your data.
    """

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        return None

    def __init__(self, candle_cluster, **options):
        """
        __init__(
            self,
            candle_cluster: oandapysuite.objects.instrument.CandleCluster,
            options: dict(), <--- Parameters for your indicator. eg. period, etc...
            )
        """
        for key, value in options.items():
            setattr(self, key, value)
        self.is_subplot = False
        self.data = self.ind_algorithm(candle_cluster, options)



class SimpleMovingAverage(BaseIndicator):

    def __ma_helper(self, candle_cluster, options):
        datapoints = []
        for i in range(len(candle_cluster)):
            if i < options['period']:
                datapoints.append(None)
                continue
            # Evil one liner 😈
            # The sum of the attribute in the `options['on'] parameter for each candle j, j in range of i - the period, divided by the period
            datapoint = sum([getattr(candle_cluster[j], options['on'])  for j in range(i-options['period'],i)])/options['period']
            datapoints.append(datapoint)
        return datapoints
    def ind_algorithm(self, candle_cluster: CandleCluster, options) -> DataFrame:
        self.valid_options = ['on', 'period', 'color','name']
        if not all([key in self.valid_options for key in options.keys()]):
            raise IndicatorOptionsError(self, f'Invalid option for indicator. Valid options are:\n{self.valid_options}')
        datapoints = self.__ma_helper(candle_cluster, options)
        data_dict = {
            'y' : self.__ma_helper(candle_cluster, options),
            'x'       : candle_cluster.history('time')
        }
        return DataFrame(data=data_dict)

class SampleStandardDeviation(BaseIndicator):

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'z', 'name']
        datapoints = []
        if not all([key in self.valid_options for key in options.keys()]):
            raise IndicatorOptionsError(self, f'Invalid option for indicator. Valid options are:\n{self.valid_options}')
        for i in range(len(candle_cluster)):
            if i < options['period']:
                datapoints.append(None)
                continue
            period_average = sum([getattr(candle_cluster[j], options['on'])  for j in range(i-options['period'],i)])/options['period']
            sum_of_diff_squares = sum([(getattr(candle_cluster[j], options['on']) - period_average) ** 2 for j in range(i-options['period'],i)])
            std = math.sqrt(sum_of_diff_squares/options['period'])
            datapoint = D(std*options['z']) + getattr(candle_cluster[i], options['on'])
            datapoints.append(datapoint)
        return DataFrame(
            data=
            {
                'x' : candle_cluster.history('time'),
                'y' : datapoints
            }
        )

class RelativeStrengthIndex(BaseIndicator):

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
            """
            Calculate Relative Strength Index (RSI) for a given period.

            Parameters:
            - period: int, Period of the RSI
            - candle_data: DataFrame, OHLC and time data stored in a pandas DataFrame

            Returns:
            - rsi_values: Series, RSI values for each corresponding time period
            """

            # Calculate daily price changes
            self.is_subplot = True
            period = options['period']
            delta = candle_cluster.to_dataframe()['close'].diff()

            # Calculate gain (positive price changes) and loss (negative price changes)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            # Calculate average gain and average loss over the specified period
            avg_gain = gain.rolling(window=period, min_periods=1).mean()
            avg_loss = loss.rolling(window=period, min_periods=1).mean()

            # Calculate relative strength (RS)
            rs = avg_gain / avg_loss

            # Calculate RSI
            rsi = 100 - (100 / (1 + rs))
            return DataFrame(
                data=
                {
                    'x' : candle_cluster.history('time'),
                    'y' : rsi
                }
            )

class PopulationStandardDeviation(BaseIndicator):

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'z', 'name']
        datapoints = []
        if not all([key in self.valid_options for key in options.keys()]):
            raise IndicatorOptionsError(self, f'Invalid option for indicator. Valid options are:\n{self.valid_options}')
        population_average = sum(candle_cluster.history(options['on']))/len(candle_cluster)
        sum_of_diff_squares = sum((getattr(candle, options['on']) - population_average) ** 2 for candle in candle_cluster)
        std = math.sqrt(sum_of_diff_squares / len(candle_cluster))
        for candle in candle_cluster:
            datapoint = D(std*options['z']) + getattr(candle, options['on'])
            datapoints.append(datapoint)
        return DataFrame(
            data=
            {
                'x' : candle_cluster.history('time'),
                'y' : datapoints
            }
        )


### My own

class StandardAverageDifference(BaseIndicator):

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'name']
        self.period = options['period']
        datapoints = []
        if not all([key in self.valid_options for key in options.keys()]):
            raise IndicatorOptionsError(self, f'Invalid option for indicator. Valid options are:\n{self.valid_options}')
        for i in range(len(candle_cluster)):
            if i < options['period']:
                datapoints.append(None)
                continue
            this_cand = getattr(candle_cluster[i], options['on'])
            differences = sum(this_cand - getattr(candle_cluster[j], options['on']) for j in range(i-options['period'], i))
            avg_diff = differences/options['period']
            normalized_diff = this_cand + (avg_diff/this_cand)
            datapoints.append((normalized_diff))
        return DataFrame(
            data=
            {
                'x' : candle_cluster.history('time'),
                'y' : datapoints
            }
        )

class AltAverageDifference(BaseIndicator):

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'name']
        self.is_subplot = True
        self.period = options['period']
        datapoints = []
        if not all([key in self.valid_options for key in options.keys()]):
            raise IndicatorOptionsError(self, f'Invalid option for indicator. Valid options are:\n{self.valid_options}')
        for i in range(len(candle_cluster)):
            if i < options['period']:
                datapoints.append(None)
                continue
            this_cand = getattr(candle_cluster[i], options['on'])
            differences = sum(this_cand - getattr(candle_cluster[j], options['on']) for j in range(i-options['period'], i))
            avg_diff = differences/options['period']
            datapoints.append((avg_diff))
        return DataFrame(
            data=
            {
                'x' : candle_cluster.history('time'),
                'y' : datapoints
            }
        )


class AverageAverageDifference(BaseIndicator):

    def ind_algorithm(self, candle_cluster: CandleCluster, options: dict) -> DataFrame:
        self.valid_options = ['on', 'period', 'color', 'name']
        stavdf = []
        datapoints = []
        avd_datapoints = []
        if not all([key in self.valid_options for key in options.keys()]):
            raise IndicatorOptionsError(self, f'Invalid option for indicator. Valid options are:\n{self.valid_options}')
        for i in range(len(candle_cluster)):
            if i < options['period']:
                avd_datapoints.append(None)
                continue
            this_cand = getattr(candle_cluster[i], options['on'])
            differences = sum(this_cand - getattr(candle_cluster[j], options['on']) for j in range(i-options['period'], i))
            avg_diff = differences/options['period']
            avd_datapoints.append((avg_diff))
            normalized_diff = this_cand + (avg_diff/this_cand)
            stavdf.append((normalized_diff))

        for i in range(len(avd_datapoints)):
            if i < 2 * options['period'] -1:
                datapoints.append(None)
                continue
            avg_diff_dp =                getattr(candle_cluster[i], options['on']) + (decimal.Decimal(
                                sum([avd_datapoints[j+1] for j in range(i-options['period'], i)])) / decimal.Decimal(options['period']))
            datapoints.append(avg_diff_dp)
        pass
        return DataFrame(
            data=
            {
                'x' : candle_cluster.history('time'),
                'y' : datapoints
            }
        )









