# creates heatmap
# x axis: period of day
# y axis: outside temp
# color: median boiler uptime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

fileName = 'bw_vl_ww'

minValueDiff = 0.05

maxTimeDiff = pd.Timedelta('60s')

# periods of the day for dividing the data
# 08:00-10:00, 10:00-12:00, 12:00-14:00, etc.
# all units in hours
t0 = 6
t1 = 22
tspan = 1

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value', 'TT_10']]

# filtering out times
df = df.loc[(df['Timestamp'].dt.hour >= t0) & (df['Timestamp'].dt.hour < t1)]

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df[['Timestamp', 'Value']].diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# for each measurement, give the date
df['Date'] = df['Timestamp'].dt.date

# for each measurement, give what period of the day it is
# periods are 0 to n
df['Period'] = df['Timestamp'].apply(
    lambda ts: np.floor((ts.hour - t0) / tspan).astype(int))

# group by each date and period
# have columns for rise times and total times
periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['Period', 'TT_10']).agg({'Time_diff': 'sum'})
periodTotal = df.groupby(['Period', 'TT_10']).agg({'Time_diff': 'sum'})
periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['Period', 'TT_10'])
periodSums.rename(columns={'Time_diff_x': 'Rises', 'Time_diff_y': 'Total'}, inplace=True)

periodRatios = periodSums['Rises'] / periodSums['Total']
periodRatios = periodRatios.unstack(level='TT_10')

# now pivot to create a 2D array where the rows are outside temp, 
# columns are hours of day, and values are uptime ratios
#pivot = periodRatios.pivot(index='TT_10', columns='Period', values='Ratio')

print(periodRatios.describe())

ax = sns.heatmap(periodRatios, cmap = "rainbow", vmax = 0.4)
ax.set_title('Boiler uptime based on ' + fileName.upper().replace('_', ' ') +
          ', by period and outside temp')
ax.set_xlabel('Outside temperature')
xtickList = [col for col in periodRatios.columns if col % 5 == 0]
ax.set_xticks([periodRatios.columns.get_loc(col) for col in xtickList])
ax.set_xticklabels(xtickList)

ax.set_ylabel(str(tspan) + ' hour periods by start hour')
ax.set_yticklabels(range(t0, t1, tspan))

plt.show()