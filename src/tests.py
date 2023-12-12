import oandapysuite
import unittest
from datetime import datetime
from numpy import dtype

### Test API functionality

class TestAPI(unittest.TestCase):

    def test_api_instantiation(self):

        api_object = oandapysuite.api.API()

        # Assert that the API object is instantiated correctly and exists
        self.assertIsNotNone(api_object)

        # Assert that the API object has the auth_header attribute
        self.assertTrue(hasattr(api_object, 'auth_header'))
        self.assertIsNotNone(api_object.auth_header)

        # Assert that the API object does not available_accounts before accounts have been loaded
        self.assertFalse(api_object.available_accounts)

        # Assert that the API object does not have a selected_account before an account has been selected
        self.assertIsNone(api_object.selected_account)

        # Assert that the API object does not have open trades before trades have been opened.
        self.assertFalse(api_object.open_trades)

    def test_get_candles(self):

        api_object = oandapysuite.api.API()

        # Runs tests on a CandleCluster object containing one M1 candle for AUD_USD.
        one_candle_test_on_M1_for_audusd = api_object.get_candles('AUD_USD', 'M1', 1)

        # Assert that the returned object is not None
        self.assertIsNotNone(one_candle_test_on_M1_for_audusd)

        # Assert that the returned object is a CandleCluster object
        self.assertIsInstance(one_candle_test_on_M1_for_audusd, oandapysuite.objects.instrument.CandleCluster)

        # Assert that the returned object has the correct instrument
        self.assertEqual(one_candle_test_on_M1_for_audusd.instrument, 'AUD_USD')

        # Assert that the returned object has the correct granularity
        self.assertEqual(one_candle_test_on_M1_for_audusd.gran, 'M1')

        # Assert that the returned object has the correct number of candles
        self.assertEqual(len(one_candle_test_on_M1_for_audusd), 1)


        # Run tests on a CandleCluster object containing 1000 M1 candles for AUD_USD.
        one_thousand_candle_test_on_M1_for_audusd = api_object.get_candles('AUD_USD', 'M1', 1000)

        # Assert that the returned object has the correct number of candles
        self.assertEqual(len(one_thousand_candle_test_on_M1_for_audusd), 1000)

        # Run tests on different time frames for 10 candles on AUD_USD.
        ten_candle_test_on_M5_for_audusd = api_object.get_candles('AUD_USD', 'M5', 10)
        ten_candle_test_on_M15_for_audusd = api_object.get_candles('AUD_USD', 'M15', 10)
        ten_candle_test_on_M30_for_audusd = api_object.get_candles('AUD_USD', 'M30', 10)
        ten_candle_test_on_H1_for_audusd = api_object.get_candles('AUD_USD', 'H1', 10)
        ten_candle_test_on_H2_for_audusd = api_object.get_candles('AUD_USD', 'H2', 10)
        ten_candle_test_on_H4_for_audusd = api_object.get_candles('AUD_USD', 'H4', 10)
        ten_candle_test_on_H8_for_audusd = api_object.get_candles('AUD_USD', 'H8', 10)
        ten_candle_test_on_H12_for_audusd = api_object.get_candles('AUD_USD', 'H12', 10)
        ten_candle_test_on_D_for_audusd = api_object.get_candles('AUD_USD', 'D', 10)
        ten_candle_test_on_W_for_audusd = api_object.get_candles('AUD_USD', 'W', 10)
        ten_candle_test_on_M_for_audusd = api_object.get_candles('AUD_USD', 'M', 10)

        # Assert that the returned objects are not None
        self.assertIsNotNone(ten_candle_test_on_M5_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_M15_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_M30_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_H1_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_H2_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_H4_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_H8_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_H12_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_D_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_W_for_audusd)
        self.assertIsNotNone(ten_candle_test_on_M_for_audusd)

        # Assert that the returned objects have the correct number of candles
        self.assertEqual(len(ten_candle_test_on_M5_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_M15_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_M30_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_H1_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_H2_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_H4_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_H8_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_H12_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_D_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_W_for_audusd), 10)
        self.assertEqual(len(ten_candle_test_on_M_for_audusd), 10)

        # Assert that the returned objects have the correct granularity
        self.assertEqual(ten_candle_test_on_M5_for_audusd.gran, 'M5')
        self.assertEqual(ten_candle_test_on_M15_for_audusd.gran, 'M15')
        self.assertEqual(ten_candle_test_on_M30_for_audusd.gran, 'M30')
        self.assertEqual(ten_candle_test_on_H1_for_audusd.gran, 'H1')
        self.assertEqual(ten_candle_test_on_H2_for_audusd.gran, 'H2')
        self.assertEqual(ten_candle_test_on_H4_for_audusd.gran, 'H4')
        self.assertEqual(ten_candle_test_on_H8_for_audusd.gran, 'H8')
        self.assertEqual(ten_candle_test_on_H12_for_audusd.gran, 'H12')
        self.assertEqual(ten_candle_test_on_D_for_audusd.gran, 'D')
        self.assertEqual(ten_candle_test_on_W_for_audusd.gran, 'W')
        self.assertEqual(ten_candle_test_on_M_for_audusd.gran, 'M')


        # Run tests on different instruments for 10 candles on M1.
        ten_candle_test_on_M1_for_audcad = api_object.get_candles('AUD_CAD', 'M1', 10)
        ten_candle_test_on_M1_for_usdcad = api_object.get_candles('USD_CAD', 'M1', 10)
        ten_candle_test_on_M1_for_eurgbp = api_object.get_candles('EUR_GBP', 'M1', 10)
        ten_candle_test_on_M1_for_audjpy = api_object.get_candles('AUD_JPY', 'M1', 10)
        ten_candle_test_on_M1_for_gbpusd = api_object.get_candles('GBP_USD', 'M1', 10)
        ten_candle_test_on_M1_for_audchf = api_object.get_candles('AUD_CHF', 'M1', 10)

        # Assert that the returned objects are not None
        self.assertIsNotNone(ten_candle_test_on_M1_for_audcad)
        self.assertIsNotNone(ten_candle_test_on_M1_for_usdcad)
        self.assertIsNotNone(ten_candle_test_on_M1_for_eurgbp)
        self.assertIsNotNone(ten_candle_test_on_M1_for_audjpy)
        self.assertIsNotNone(ten_candle_test_on_M1_for_gbpusd)
        self.assertIsNotNone(ten_candle_test_on_M1_for_audchf)


        # Run tests on get_candles(_from, _to) on H1 for AUD_USD.
        start1 = oandapysuite.objects.datatypes.UnixTime("2010-01-05")
        start2 = oandapysuite.objects.datatypes.UnixTime("2015-01-06")
        start3 = oandapysuite.objects.datatypes.UnixTime("2020-01-07")
        start4 = oandapysuite.objects.datatypes.UnixTime("2010-01-05 13:00")
        start5 = oandapysuite.objects.datatypes.UnixTime("2015-01-06 13:00")
        start6 = oandapysuite.objects.datatypes.UnixTime("2020-01-07 13:00")
        end1 = oandapysuite.objects.datatypes.UnixTime("2010-01-06")
        end2 = oandapysuite.objects.datatypes.UnixTime("2015-01-07")
        end3 = oandapysuite.objects.datatypes.UnixTime("2020-01-08")
        end4 = oandapysuite.objects.datatypes.UnixTime("2010-01-06 13:00")
        end5 = oandapysuite.objects.datatypes.UnixTime("2015-01-07 13:00")
        end6 = oandapysuite.objects.datatypes.UnixTime("2020-01-08 13:00")

        one_day_test_on_H1_for_audusd_start1_end1 = api_object.get_candles('AUD_USD', 'H1', _from=start1, to=end1)
        one_day_test_on_H1_for_audusd_start2_end2 = api_object.get_candles('AUD_USD', 'H1', _from=start2, to=end2)
        one_day_test_on_H1_for_audusd_start3_end3 = api_object.get_candles('AUD_USD', 'H1', _from=start3, to=end3)
        one_day_test_on_H1_for_audusd_start4_end4 = api_object.get_candles('AUD_USD', 'H1', _from=start4, to=end4)
        one_day_test_on_H1_for_audusd_start5_end5 = api_object.get_candles('AUD_USD', 'H1', _from=start5, to=end5)
        one_day_test_on_H1_for_audusd_start6_end6 = api_object.get_candles('AUD_USD', 'H1', _from=start6, to=end6)
        pass

        # Assert that the returned objects have the correct number of candles (24)
        self.assertEqual(len(one_day_test_on_H1_for_audusd_start1_end1), 24)
        self.assertEqual(len(one_day_test_on_H1_for_audusd_start2_end2), 24)
        self.assertEqual(len(one_day_test_on_H1_for_audusd_start3_end3), 24)
        self.assertEqual(len(one_day_test_on_H1_for_audusd_start4_end4), 24)
        self.assertEqual(len(one_day_test_on_H1_for_audusd_start5_end5), 24)
        self.assertEqual(len(one_day_test_on_H1_for_audusd_start6_end6), 24)

    def test_get_child_candles(self):

        api_object = oandapysuite.api.API()

        # Runs tests on a CandleCluster object containing one M1 candle for AUD_USD.
        test_M_candle_for_audusd = api_object.get_candles('AUD_USD', 'M', 1)[0]

        test_D_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'D')
        test_W_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'W')
        test_H12_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'H12')
        test_H8_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'H8')
        test_H4_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'H4')
        test_H2_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'H2')
        test_H1_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'H1')
        test_M30_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'M30')
        test_M15_child_candles_for_audusd = api_object.get_child_candles(test_M_candle_for_audusd, 'M15')

        # Assert that the returned CandleClusters are not empty
        self.assertFalse(test_D_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_W_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_H12_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_H8_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_H4_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_H2_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_H1_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_M30_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_M15_child_candles_for_audusd.candles.empty)

        # Run child candle tests on a lower timeframe
        test_H1_child_candles_for_audusd = api_object.get_candles('AUD_USD', 'H1', 1)

        test_M30_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'M30')
        test_M15_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'M15')
        test_M5_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'M5')
        test_M1_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'M1')
        test_S30_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'S30')
        test_S15_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'S15')
        test_S5_child_candles_for_audusd = api_object.get_child_candles(test_H1_child_candles_for_audusd, 'S5')

        # Assert that the returned CandleClusters are not empty
        self.assertFalse(test_M30_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_M15_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_M5_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_M1_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_S30_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_S15_child_candles_for_audusd.candles.empty)
        self.assertFalse(test_S5_child_candles_for_audusd.candles.empty)

    def test_load_and_select_accounts(self):

        api_object = oandapysuite.api.API()
        api_object.load_accounts()
        api_object.select_account()

        # Assert that the API object has available_accounts after accounts have been loaded
        self.assertTrue(api_object.available_accounts)

        # Assert that the API object has a selected_account after an account has been selected
        self.assertIsNotNone(api_object.selected_account)

    def test_unix_time_objects(self):

        # Create UnixTime objects for different times
        ut1 = oandapysuite.objects.datatypes.UnixTime("2023-12-01")
        ut2 = oandapysuite.objects.datatypes.UnixTime("2023-12-01 00:00")
        ut3 = oandapysuite.objects.datatypes.UnixTime("2023-12-01 18:00")
        ut5 = oandapysuite.objects.datatypes.UnixTime("2005-01-01 06:00")
        ut6 = oandapysuite.objects.datatypes.UnixTime("1970-01-02 00:00")

        # Assert that the UnixTime objects have the correct timestamp
        self.assertEqual(ut1.timestamp, 1701406800)
        self.assertEqual(ut2.timestamp, 1701406800)
        self.assertEqual(ut3.timestamp, 1701471600)
        self.assertEqual(ut5.timestamp, 1104555600)
        self.assertEqual(ut6.timestamp, 104400)

    def test_indicators(self):

        # Create an API object
        api_object = oandapysuite.api.API()

        # Create a CandleCluster object
        candles = api_object.get_candles('AUD_USD', 'M1', 1000)

        sma = oandapysuite.objects.indicators.SimpleMovingAverage(on='close', period=50, color='purple', name='sma 100')
        stdforprice = oandapysuite.objects.indicators.SampleStandardDeviation(on='close', period=50, color='orange', name='std 60')
        zscore = oandapysuite.objects.indicators.ZScoreOfPrice(on='close', period=50, color='black', name='zscore')

        # Assert that the indicators do not have data before data has been loaded
        self.assertTrue(sma.data.empty)
        self.assertTrue(stdforprice.data.empty)
        self.assertTrue(zscore.data.empty)

        # Load data into the indicators
        sma.update(candles)
        stdforprice.update(candles)
        zscore.update(candles)
        indicators = [sma, stdforprice, zscore]

        # Assert that the indicators have data after data has been loaded and that the data types are correct
        for indicator in indicators:
            for row in indicator.data.iterrows():
                self.assertIsInstance(row[1]['y'], float)
                self.assertIsInstance(row[1]['x'], datetime)
                self.assertIsInstance(row[1]['candles'], oandapysuite.objects.instrument.CandleCluster.Candle)





if __name__ == '__main__':
    unittest.main()