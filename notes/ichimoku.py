__author__ = 'nii236'
import pandas as pd

data = pd.read_csv("spy_with_ichimoku.csv")
high_prices = data['High']
low_prices = data['Low']
close_prices = data['Close']
open_prices = data['Open']
dates = data['Date']

# Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
period9_high = pd.rolling_max(high_prices, window=9)
period9_low = pd.rolling_min(low_prices, window=9)
tenkan_sen = (period9_high + period9_low) / 2

# Kijun-sen (Base Line): (26-period high + 26-period low)/2))
period26_high = pd.rolling_max(high_prices, window=26)
period26_low = pd.rolling_min(low_prices, window=26)
kijun_sen = (period26_high + period26_low) / 2

# Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

# Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
period52_high = pd.rolling_max(high_prices, window=52)
period52_low = pd.rolling_min(low_prices, window=52)
senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

# The most current closing price plotted 22 time periods behind (optional)
chikou_span = close_prices.shift(-22) # 22 according to investopedia

# frames = [tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b]
# df = pd.concat(frames)
# print(df)

data = pd.DataFrame({'idx_col': dates, 'Open':open_prices, 'High': high_prices, 'Low':low_prices, 'Close':close_prices, 'Tenkan': tenkan_sen,'Kijun':kijun_sen, 'Senkou A': senkou_span_a, 'Senkou B': senkou_span_b})
data = data[['idx_col', 'Open', 'High', 'Low', 'Close', 'Tenkan', 'Kijun', 'Senkou A', 'Senkou B']]
# print(data)
data.to_csv('output.csv')
