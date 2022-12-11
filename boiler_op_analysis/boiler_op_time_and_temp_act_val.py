# x axis: minutes rise
# y axis: temperatures. vertical line between min and max temp for each rise period.

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

fileName = 'bw_vl_hzg'

minValueDiff = 0.05

maxTimeDiff = pd.Timedelta('30s')

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value']]

df[['Time_diff', 'Value_diff']] = df.diff()

# observations where the temperature is rising
rises = df.loc[df['Value_diff'] >= minValueDiff]

rises['Time_diff'] = rises['Timestamp'].diff()

rises = rises.loc[(rises['Time_diff'] <= maxTimeDiff) | (
    rises['Time_diff'].shift(-1) < maxTimeDiff)].reset_index(drop=True)

# list of indexes of observations marking the start of a rising period
# because the time difference is large but it is rising
risesIdx0 = rises.loc[rises['Time_diff'] > maxTimeDiff].index.tolist()
risesIdx1 = risesIdx0[1:-1]

risesIdx0.pop() # remove last element of the list because we don't need it

rises_grouped = []

for idx0, idx1 in zip(risesIdx0, risesIdx1):

    # select a period df.iloc[row, col]
    rise = rises.iloc[idx0+1:idx1, :]

    # append the grouped period representing the rise
    rise_agg = rise[['Value','Time_diff']].agg({'Time_diff': 'sum'})
    rise_agg['Max'] = rise['Value'].max()
    rise_agg['Min'] = rise['Value'].min()

    rises_grouped.append(rise_agg)

rises_grouped = pd.DataFrame(pd.concat(rises_grouped, axis = 1)).transpose()

rises_grouped['Time_diff'] = (rises_grouped['Time_diff'] / np.timedelta64(1, 'm'))
rises_grouped[['Max', 'Min']] = rises_grouped[['Max', 'Min']].apply(np.float64)

rises_grouped = rises_grouped[rises_grouped['Max'] - rises_grouped['Min'] != 0.0]

print(rises_grouped)

fig, ax = plt.subplots()

for x, idx in zip(rises_grouped.loc[1:,'Time_diff'], rises_grouped.index):
    y2 = rises_grouped.loc[idx,:]['Max']
    y1 = rises_grouped.loc[idx,:]['Min']
    ax.plot([x, x], [y1, y2], color = 'black', marker = 'o', markersize = 3)

ax.set_title(str(fileName).upper().replace('_',' ') + ' periods of rising temperatures')
#ax.set_xlim(0, 5)
ax.set_xlabel('Length of period (minutes)')
ax.set_ylabel('Max and min temperature in period (deg C)')

plt.show()