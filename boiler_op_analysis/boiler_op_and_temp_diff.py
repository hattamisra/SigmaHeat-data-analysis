# compares boiler uptime ratio to how temps change over time

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

begin_runtime = dt.datetime.now()

fileName = 'bw_vl_hzg'

minValueDiff = 0.05

maxTimeDiff = pd.Timedelta('30s')

period = '5min'

minTempDiff = 0

path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value']]

df[['Time_diff', 'Value_diff']] = df.diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# categorise each measurement as part of a period
df.insert(0, 'Period', pd.DatetimeIndex(df['Timestamp']).floor(period))

# group by each date and period
# have columns for rise times and total times
periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['Period'])['Time_diff'].sum()
periodTotal = df.groupby(['Period'])['Time_diff'].sum()
periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['Period'])
periodSums.columns = ['Rises', 'Total']
periodSums['Ratio'] = periodSums['Rises'] / periodSums['Total']

# sort out max and min temps by period
maxIdx = df.loc[df.groupby('Period', as_index = False)['Value'].idxmax()['Value'], :][['Period', 'Timestamp', 'Value']]
maxIdx['Idx'] = maxIdx.index
minIdx = df.loc[df.groupby('Period', as_index = False)['Value'].idxmin()['Value'], :][['Period', 'Timestamp', 'Value']]
minIdx['Idx_min'] = minIdx.index
minIdx = minIdx.rename(columns = {'Timestamp': 'Timestamp_min', 'Value': 'Value_min'})

# now merge 
MaxMinIdx = maxIdx.merge(minIdx, on=['Period'])
MaxMinIdx['Temp_diff'] = MaxMinIdx['Value'] - MaxMinIdx['Value_min']
MaxMinIdx = MaxMinIdx.set_index('Period')

periodSums = periodSums.join(MaxMinIdx['Temp_diff'])
periodSums = periodSums.loc[periodSums['Temp_diff'] > minTempDiff]

fig, ax = plt.subplots()
x = periodSums['Ratio']
y = periodSums['Temp_diff']

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 1}, line_kws={"color": "red"})
ax.set(xlabel = 'Boiler uptime ratio', ylabel = 'Temp difference (C)')

plt.title('Boiler uptime ratio and temperature difference, minimum temp diff ' + str(minTempDiff) + ' deg C')

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()