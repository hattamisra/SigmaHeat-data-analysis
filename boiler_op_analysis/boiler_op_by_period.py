# Looks at times where the temps are rising
# because that's when the boiler is operating

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.stats as stats

# changeable parameters
fileName = 'bw_rl_ww'  # name of file where we get the data (excl extension)

# filter out the noise (small fluctuations caused by measure errors)
minValueDiff = 0.05  # if value2 - value1 > minValueDiff

# filters out the times without regular measurements
maxTimeDiff = pd.Timedelta('30s')

# periods of the day for dividing the data
# 08:00-10:00, 10:00-12:00, 12:00-14:00, etc.
# all units in hours
t0 = 0
t1 = 24
tspan = 1

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value']]

# filtering out times that we don't care about (i.e. when people are asleep)
df = df.loc[(df['Timestamp'].dt.hour >= t0) & (df['Timestamp'].dt.hour < t1)]

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df.diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# for each measurement, give the date
df['Date'] = df['Timestamp'].dt.date

# for each measurement, give what period of the day it is
# periods are 0 to n
df['Period'] = df['Timestamp'].apply(
    lambda ts: np.floor((ts.hour - t0) / tspan).astype(int))

#df = df.groupby(by = df['Timestamp'].dt.hour)['Time_diff'].sum()

# group by each date and period
# have columns for rise times and total times
periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['Date', 'Period'])['Time_diff'].sum()
periodTotal = df.groupby(['Date', 'Period'])['Time_diff'].sum()
periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['Date', 'Period'])
periodSums.columns = ['Rises', 'Total']
periodSums['Ratio'] = periodSums['Rises'] / periodSums['Total']

nPeriods = np.floor((t1 - t0)/tspan).astype(int)
ratioByPeriod = [periodSums.xs(period, level=1)['Ratio'] for period in range(nPeriods)]

print([len(p) for p in ratioByPeriod])

# stats
# * unpacks list to feed each item as a different arg in the function
F, p = stats.f_oneway(*ratioByPeriod)
print(fileName.upper().replace('_',' ') + ', F = ' + round(F, 3).astype(str) + ', p-value = ' + round(p, 3).astype(str))

# plotting

fig, ax = plt.subplots()

ax.boxplot(ratioByPeriod)
ax.set_xticklabels(np.arange(t0, t1, tspan))
plt.title('Boiler uptime based on ' + fileName.upper().replace('_', ' ') +
          ', by period')
plt.xlabel(str(tspan) + ' hour periods by start hour')
plt.ylabel('Boiler uptime / total time')
plt.show()