# Looks at times where the temps are rising
# because that's when the boiler is operating
# organise by outside temperature (current temp, or 10 min before, or 30...)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import os

# check runtime
begin_runtime = dt.datetime.now()

# changeable parameters
fileName = 'bw_vl_hzg'  # name of file where we get the data (excl extension)

# filter out the noise (small fluctuations caused by measure errors)
minValueDiff = 0.05  # if value2 - value1 > minValueDiff

# filters out the times without regular measurements
maxTimeDiff = pd.Timedelta('30s')

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df[['Timestamp', 'Value']].diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# for every 10-min period, get rising time and total time
# only need to get TT_10 once
periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['Timestamp_10min']).agg({'Time_diff': 'sum'})
periodTotal = df.groupby(['Timestamp_10min']).agg({'Time_diff': 'sum', 'TT_10': 'first'}) 
periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['Timestamp_10min'], copy = False)
periodSums.columns = ['Rises', 'Total', 'TT_10']
periodSums.insert(len(periodSums.columns)-1, 'Ratio', (periodSums['Rises'] / periodSums['Total']))

temps = np.arange(0, 35, 1)

ratioByTemp = [periodSums.loc[periodSums['TT_10'].round() == temp]['Ratio'] for temp in temps]
print([len(p) for p in ratioByTemp])

# plotting

fig, ax = plt.subplots()

ax.boxplot(ratioByTemp, showfliers=False)
ax.set_xticklabels(temps)
plt.title(fileName.upper().replace('_', ' ') +
          ' boiler uptime ratios by outside temperature')
plt.xlabel('Outside temperature (deg C)')
plt.ylabel('Boiler uptime / total time')

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()