import pandas as pd
import os
import statsmodels.tsa.holtwinters as holtwinters
import matplotlib.pyplot as plt

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

# remove rows with duplicated indices (duplicate timestamp observations)
df = df[~df.index.duplicated()]

# filter for month
df = df.loc[df['Timestamp'].dt.month == 5]

#df = df.set_index('Timestamp')
#df.index = pd.DatetimeIndex(df.index).to_period('min')

# separate data into train and test 
df_train = df.loc[df['Timestamp'].dt.day < 7].copy()
df_test = df.loc[df['Timestamp'].dt.day >= 7].copy()

# forecast models
df_test['mvavg'] = df['Value'].rolling(60).mean().iloc[-1]

hwss1 = holtwinters.SimpleExpSmoothing(df_train['Value']).fit()
df_test['hwss1'] = hwss1.forecast(len(df_test))

hwes = holtwinters.ExponentialSmoothing(df_train['Value'], seasonal_periods = 7, seasonal = 'add').fit()
df_test['hwes'] = hwes.forecast(len(df_test))

print(df_train['Value'])

plt.plot(df_train['Value'], label = 'Train')
plt.plot(df_test['Value'], label = 'Test')
plt.plot(df_test['mvavg'], label = 'mv avg')
plt.plot(df_test['hwes'], label = 'hwes')
plt.legend()
plt.show()