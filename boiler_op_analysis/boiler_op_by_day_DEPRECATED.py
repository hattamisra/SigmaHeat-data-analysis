# IGNORE THIS FILE
# USE boiler_op_by_period.py INSTEAD

# Looks at times where the temps are rising
# because that's when the boiler is operating

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.stats as stats

# changeable parameters
fileName = 'bw_vl_hzg'  # name of file where we get the data (excl extension)

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

# this MUST be the full name, because we call the .day_name() function later on
listOfDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

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
df['Day'] = df['Timestamp'].dt.day_name()

#df = df.groupby(by = df['Timestamp'].dt.hour)['Time_diff'].sum()

# group by each date and period
# have columns for rise times and total times
periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['Date', 'Day'])['Time_diff'].sum()
periodTotal = df.groupby(['Date', 'Day'])['Time_diff'].sum()
periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['Date', 'Day'])
periodSums.columns = ['Rises', 'Total']
periodSums['Ratio'] = periodSums['Rises'] / periodSums['Total']

nPeriods = np.floor((t1 - t0)/tspan).astype(int)
ratioByDay = [periodSums.xs(day, level=1)['Ratio'] for day in listOfDays]

# how many data points for each day?
print([len(day) for day in ratioByDay])

# stats
# * unpacks list to feed each item as a different arg in the function
print(stats.f_oneway(*ratioByDay))

# plotting

fig, ax = plt.subplots()

ax.boxplot(ratioByDay)
ax.set_xticklabels(listOfDays)
plt.title(fileName.upper().replace('_', ' ') +
          ' boiler uptime ratios by day')
plt.xlabel(str(tspan) + ' hour periods by start hour')
plt.ylabel('Boiler uptime / total time')
plt.show()