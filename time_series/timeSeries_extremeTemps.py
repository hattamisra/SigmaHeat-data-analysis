# when there is a 1.0 uptime ratio, look at how temps changed 5 min before & after
# graph all system component temperatures as a time series

import pandas as pd
import os
from matplotlib import pyplot as plt
import datetime as dt

begin_runtime = dt.datetime.now()

# for uptime, filter out the noise (small fluctuations caused by measure errors)
minTempDiff = 0.05  # if value2 - value1 > minValueDiff

# filters out the times without regular measurements
maxTimeDiff = pd.Timedelta('30s')

period = '5min'

# read the entire dataframe
path = os.path.join('data', 'withWeather', 'data_with_weather_2021-08-24.csv')
df_all = pd.read_csv(path, parse_dates=['Timestamp'])

# separate the bw_vl_hzg for the uptime analysis
df = df_all.loc[df_all['Name'] == 'BW VL Hzg'][[
    'Timestamp', 'Value']]  # MeasurementId = 12

# Differences column
# Time_diff: length of time from prev measurement of that system
# Value_diff: value difference from prev measurement of that system
df[['Time_diff', 'Temp_diff']] = df.diff()

# filter out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# categorise each measurement as part of a period
df.insert(0, 'Period', pd.DatetimeIndex(df['Timestamp']).floor(period))

#df = df.groupby(by = df['Timestamp'].dt.hour)['Time_diff'].sum()

# group by each date and period
# have columns for rise times and total times
periodRises = df.loc[df['Temp_diff'] >= minTempDiff].groupby(['Period'])[
    'Time_diff'].sum()
periodTotal = df.groupby(['Period'])['Time_diff'].sum()
periodSums = pd.merge(periodRises, periodTotal, how='left', on=['Period'])
periodSums.columns = ['Rises', 'Total']
periodSums['Ratio'] = periodSums['Rises'] / periodSums['Total']

# sort out max and min temps by period
maxIdx = df.loc[df.groupby('Period', as_index=False)['Value'].idxmax()[
    'Value'], :][['Period', 'Timestamp', 'Value']]
maxIdx['Idx'] = maxIdx.index
minIdx = df.loc[df.groupby('Period', as_index=False)['Value'].idxmin()[
    'Value'], :][['Period', 'Timestamp', 'Value']]
minIdx['Idx_min'] = minIdx.index
minIdx = minIdx.rename(
    columns={'Timestamp': 'Timestamp_min', 'Value': 'Value_min'})

# now merge
MaxMinIdx = maxIdx.merge(minIdx, on=['Period'])
MaxMinIdx['Temp_diff'] = MaxMinIdx['Value'] - MaxMinIdx['Value_min']
MaxMinIdx = MaxMinIdx.set_index('Period')

periodSums = periodSums.join(MaxMinIdx['Temp_diff'])
periodSums = periodSums.loc[periodSums['Temp_diff'] > minTempDiff]

# print(len(periodSums.loc[periodSums['Ratio'] == 1.0]))
# print(len(periodSums.loc[(periodSums['Ratio'] == 1.0) & (periodSums['Temp_diff'] > 5)]))

# pick a random period to look at
# to_datetime for changing from DatetimeIndex to Datetime
samplePeriod = (periodSums.loc[(periodSums['Ratio'] == 1.0) & (periodSums['Temp_diff'] > 5)]
                .sample().index)

samplePeriod = samplePeriod[0]

print(samplePeriod)

# plot temps 5 min before and 10 min after the period start time
t_neg = dt.timedelta(minutes = 5)
t_pos = dt.timedelta(minutes = 10)

measurePts = {'bw_rl_hzg': 5,
              'bw_vl_hzg': 12,
              'bw_rl_ww': 6,
              'bw_vl_ww': 7,
            #   'solar_vl': 8,
            #   'solar_rl': 9,
            #   'ww_mixed': 10,
            #   'ww_unmixed': 11
              }

fig = plt.figure(figsize=(14,8))

for name in measurePts:
    measureID = measurePts[name]
    sysData = df_all.loc[(df_all['MeasurementId'] == measureID)]
    sysData = sysData.loc[(sysData['Timestamp'] >= samplePeriod - t_neg) & 
    (sysData['Timestamp'] <= samplePeriod + t_pos)]
    plt.plot(sysData['Timestamp'], sysData['Value'], linestyle = 'solid', marker = 'o', label = name)

plt.title('Timeseries around ' + str(samplePeriod))
plt.legend()
print(os.getcwd())
plt.savefig(os.path.join('Figures', 'timeGraphs', str(samplePeriod).replace(':','')), dpi = 300, orientation = 'landscape')

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()