# check for stationarity of the data

import pandas as pd
import matplotlib.pyplot as plt
import os
import statsmodels.tsa.stattools as tsatools

fileName = 'bw_vl_hzg'

# filter out the noise (small fluctuations caused by measure errors)
minValueDiff = 0 #0.05  # if value2 - value1 > minValueDiff

# filters out the times without regular measurements
maxTimeDiff = pd.Timedelta('30s')

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value', 'TT_10']]

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df[['Timestamp', 'Value']].diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# round to the nearest period
df['Period'] = df['Timestamp'].dt.round(freq='10s')

# filter for month
df = df.loc[df['Timestamp'].dt.month == 5]

# adfuller: augmented dickey-fuller test, difference stationarity test
# Null hypothesis: series is non stationary
# Alternative hypothesis: process is difference stationary
df_stationarity_adf = tsatools.adfuller(df['Value'], autolag = 'AIC')
df_adf_output = pd.Series(df_stationarity_adf[0:4], index=['Test statistic','p-value','# Lags used','# observations used'])
for key,value in df_stationarity_adf[4].items():
    df_adf_output['Critical value (%s)'%key] = value
print(df_adf_output)

# Kwiatkowski-Phillips-Schmidt-Shin Test
# Null hypothesis: Process is trend stationary / stationary around a constant
df_stationarity_kpss = tsatools.kpss(df['Value'], regression = 'c')
df_kpss_output = pd.Series(df_stationarity_kpss[0:3], index=['Test statistic','p-value','# Lags used'])
for key,value in df_stationarity_kpss[3].items():
    df_kpss_output['Critical value (%s)'%key] = value
print(df_kpss_output)

# set the timestamp as the index to allow for .shift()
df = df.set_index('Period')

# remove rows with duplicated indices (duplicate timestamp observations)
df = df[~df.index.duplicated()]

# have a value subtracted by the value from this time yesterday
df['Value_day_diff'] = df['Value'] - df['Value'].shift(periods=1, freq='D')

plt.plot(df.index, df['Value_day_diff'])
plt.show()

# from statsmodels.graphics.tsaplots import plot_pacf
# pacf = plot_pacf(df['Timestamp'], lags=25)
# plt.show()

# The ADF p-value is less than 0.05, meaning that we reject the null hypothesis for that
# meaning that it is difference stationary

# The KPSS p-value is less than 0.05, meaning that we reject the null hypothesis
# and the series is not trend stationary