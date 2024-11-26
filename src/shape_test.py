import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.optimizers import Adam
from oandapysuite import api
from oandapysuite.objects.indicators.trend import ExponentialMovingAverage
from oandapysuite.objects.indicators.volatility import AverageTrueRange
from oandapysuite.objects.indicators.momentum import RelativeStrengthIndex


def shape_test():
    cands = api.API().get_candles('GBP_USD', 'M5', count=800)
    ema_short = ExponentialMovingAverage(on='close', period=9, name='ema_short')
    ema_long = ExponentialMovingAverage(on='close', period=12, name='ema_long')
    rsi = RelativeStrengthIndex(on='close', period=24)
    atr = AverageTrueRange(period=12)

    ema_short.update(cands)
    ema_long.update(cands)
    rsi.update(cands)
    atr.update(cands)

    ema_short.data['y'].fillna(method='bfill', inplace=True)
    ema_long.data['y'].fillna(method='bfill', inplace=True)
    rsi.data['y'].fillna(method='bfill', inplace=True)
    atr.data['y'].fillna(method='bfill', inplace=True)

    cand_df = cands.to_dataframe()

    test_data = pd.DataFrame({
        'open': cand_df['open'].values,
        'high': cand_df['high'].values,
        'low': cand_df['low'].values,
        'close': cand_df['close'].values,
        'ema_short': ema_short.data['y'].values,
        'ema_long': ema_long.data['y'].values,
        'rsi': rsi.data['y'].values,
        'atr': atr.data['y'].values
    })


    test_data['Target'] = (test_data['close'].shift(-3) - test_data['close'])
    test_data.dropna(inplace=True)

    features = test_data[['open', 'high', 'low', 'close', 'ema_short', 'ema_long', 'rsi', 'atr']].values
    target = test_data['Target'].values

    scaler = MinMaxScaler(feature_range=(-1,1))
    scaled_features = scaler.fit_transform(features)

    n_candles = 12
    X = []
    y = []

    for i in range(len(scaled_features) - n_candles):
        X.append(scaled_features[i:i+n_candles])
        if i + n_candles < len(scaled_features):
            y.append(target[i+n_candles])

    X = np.array(X)
    y = np.array(y)
    return X, y