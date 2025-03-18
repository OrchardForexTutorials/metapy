import pandas as pd
import pandas_ta as ta

# Define Simple Moving Average (SMA) function
def sma(data, period):
    return ta.sma(pd.Series(data), length = period).to_numpy()

def rsi(data, period):
    return ta.rsi(ta.Series(data), period).to_numpy()
