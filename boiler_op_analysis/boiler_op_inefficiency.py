# Condensing boilers are inefficient when the return water is at a high temperature
# Inefficiency level = a*ratio + b*BW_RL_HZG, where a and b are constants
# More specific efficiency levels can be found if we know eff. curve of the boiler

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import os

# check runtime
begin_runtime = dt.datetime.now()

# inefficiency level constants - must be positive
# Inefficiency level = a*ratio + b*BW_RL_HZG
C_ratio = 1 
C_retrn = 0.1

vl_file = 'bw_vl_hzg'
rl_file = 'bw_rl_hzg'
minValueDiff = 0.05
maxTimeDiff = pd.Timedelta('30s')

vl_path = os.path.join('data', 'withWeather', vl_file + '.csv')
df = pd.read_csv(vl_path, parse_dates=['Timestamp'])

rl_path = os.path.join('data', 'withWeather', rl_file + '.csv')
rl = pd.read_csv(rl_path, parse_dates=['Timestamp'])

df['Value_RL'] = rl['Value']

# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df[['Timestamp', 'Value']].diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['Timestamp_10min']).agg({'Time_diff': 'sum'})
periodTotal = df.groupby(['Timestamp_10min']).agg({'Time_diff': 'sum', 'TT_10': 'first', 'Value_RL': 'mean'}) 
periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['Timestamp_10min'], copy = False)
periodSums.columns = ['Rises', 'Total', 'TT_10', 'Value_RL']
periodSums.insert(len(periodSums.columns)-1, 'Ratio', (periodSums['Rises'] / periodSums['Total']))
periodSums['Ineff'] = (C_ratio*periodSums['Ratio'] + C_retrn*periodSums['Value_RL']) # rounding for plotting speed
periodSums.index = pd.to_datetime(periodSums.index)

print(periodSums)

periodSumPlot = periodSums.loc[(periodSums.index.month == 5) & (periodSums.index.day == 15)]

fig, ax1 = plt.subplots()
ax1.plot(periodSumPlot['Ineff']/periodSumPlot['Ineff'].max(), label = 'Inefficiency')
ax1.plot(periodSumPlot['Ratio'], label = 'Ratio')
ax1.set_xlabel('Date')
ax1.set_ylabel('Ineff / Op Ratio')

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(periodSumPlot['Value_RL'], label = 'RL Temp', color = 'green')
ax2.set_ylabel(rl_file.upper().replace('_',' ') + ' temperature')

fig.legend(loc='center', bbox_to_anchor=(0.5, 0., 0.5, 1)) # (x, y, width, height)

plt.show()