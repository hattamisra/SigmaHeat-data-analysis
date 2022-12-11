# The lower the temperature of the RL HZG, the higher efficiency the boiler
# organise by outside temperature
# eff = -1*(RL - min(RL)) + (max(RL) - min(RL))/(max(RL) - min(RL))
# plot eff*ratio

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import os

# check runtime
begin_runtime = dt.datetime.now()

# changeable parameters
vl_file = 'bw_vl_hzg'  # name of file where we get the data (excl extension)
rl_file = 'bw_rl_hzg'

# filter out the noise (small fluctuations caused by measure errors)
minValueDiff = 0.05  # if value2 - value1 > minValueDiff

# filters out the times without regular measurements
maxTimeDiff = pd.Timedelta('30s')

# creation of dataframe
vl_path = os.path.join('data', 'withWeather', vl_file + '.csv')
df = pd.read_csv(vl_path, parse_dates=['Timestamp'])

rl_path = os.path.join('data', 'withWeather', rl_file + '.csv')
df['RL'] = pd.read_csv(rl_path, parse_dates=['Timestamp'])['Value']

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df[['Timestamp', 'Value']].diff()

# filtering out times without regular measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# for every 10-min period, get rising time and total time
# only need to get TT_10 once
rises = df.loc[df['Value_diff'] >= minValueDiff].groupby(
    ['Timestamp_10min']).agg({'Time_diff': 'sum'})
totals = df.groupby(['Timestamp_10min']).agg(
    {'Time_diff': 'sum', 'TT_10': 'first', 'RL': 'mean'})
sums = pd.merge(rises, totals, how='left', on=['Timestamp_10min'], copy=False)
sums.columns = ['Rises', 'Total', 'TT_10', 'RL']

# eff = -1*(RL - min(RL)) + (max(RL) - min(RL))/(max(RL) - min(RL))
maxRL = max(sums['RL'])
minRL = min(sums['RL'])
sums['Eff'] = (maxRL - sums['RL']) / (maxRL - minRL)
sums['Ratio'] = sums['Rises'] / sums['Total']
sums['eff*rat'] = sums['Eff'] * sums['Ratio']

# # group by temperatures
# # have columns for rise times and total times
# periodRises = df.loc[df['Value_diff'] >= minValueDiff].groupby(['TT_10_round', 'Timestamp'])['Time_diff'].sum()
# periodTotal = df.groupby(['TT_10_round', 'Timestamp'])['Time_diff'].sum()
# periodSums = pd.merge(periodRises, periodTotal, how = 'left', on = ['TT_10_round'])
# periodSums.columns = ['Rises', 'Total']
# periodSums['Ratio'] = periodSums['Rises'] / periodSums['Total']

temps = np.arange(0, 35, 1)

minRatio = 0.2
effByTemp = [sums.loc[(sums['TT_10'].round() == temp) & (sums['Ratio'] >= minRatio)]['Eff']
                for temp in temps]
print([len(p) for p in effByTemp])
print(sums.sample(10))

# plotting

fig, ax = plt.subplots()

ax.boxplot(effByTemp, showfliers=False)
ax.set_xticklabels(temps)
plt.title('Efficiency by outside temperature, minimum uptime of ' + str(minRatio))
plt.xlabel('Outside temperature (deg C)')
plt.ylabel('Efficiency')

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()
