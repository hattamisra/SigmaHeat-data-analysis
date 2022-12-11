# differenced

import pandas as pd
import matplotlib.pyplot as plt
import os
import statsmodels.tsa.stattools as tsatools

fileName = 'bw_vl_hzg'

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value', 'TT_10']]

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df[['Timestamp', 'Value']].diff()

# round to the nearest period
df['Period'] = df['Timestamp'].dt.round(freq='10s')

df = df.loc[df['Timestamp'].dt.month == 5]

# set the timestamp as the index to allow for .shift()
df = df.set_index('Period')

# remove rows with duplicated indices (duplicate timestamp observations)
df = df[~df.index.duplicated()]

# have a value subtracted by the value from this time yesterday
df['Value_day_diff'] = df['Value'] - df['Value'].shift(periods=1, freq='D')

# adfuller: augmented dickey-fuller test, difference stationarity test
# Null hypothesis: series is non stationary
# Alternative hypothesis: process is difference stationary

# Kwiatkowski-Phillips-Schmidt-Shin Test
# Null hypothesis: Process is trend stationary / stationary around a constant
df_stationarity_kpss = tsatools.kpss(df['Value_day_diff'], regression = 'c')
df_kpss_output = pd.Series(df_stationarity_kpss[0:3], index=['Test statistic','p-value','# Lags used'])
for key,value in df_stationarity_kpss[3].items():
    df_kpss_output['Critical value (%s)'%key] = value
print(df_kpss_output)

plt.plot(df.index, df['Value_day_diff'])
plt.show()