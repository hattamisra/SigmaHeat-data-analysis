# correlates time in which things rise to the temperature difference in that rise
# looks at extreme values, e.g. BW VL HZG rise at least 15 min, at most 15 C
# plots timeseries of all those values
# ideally 3 or fewer

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as dates

minValueDiff = 0.05

maxTimeDiff = pd.Timedelta('30s')

# dataframe for all data
path_all = os.path.join('data', 'withWeather', 'data_with_weather_2021-08-24.csv')
df_all = pd.read_csv(path_all, parse_dates=['Timestamp'])

# creation of dataframe
df = df_all.loc[df_all['Name'] == 'BW VL Hzg'][['Timestamp', 'Value']]

print(df)

df[['Time_diff', 'Value_diff']] = df.diff()

# observations where the temperature is rising
rises = df.loc[df['Value_diff'] >= minValueDiff]

rises['Time_diff'] = rises['Timestamp'].diff()

rises = rises.loc[(rises['Time_diff'] <= maxTimeDiff) | (
    rises['Time_diff'].shift(-1) < maxTimeDiff)].reset_index(drop=True)

# print(rises.loc[(rises.index >= 4) & (rises.index < 25)])
# print(rises.iloc[0:20, :])

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
    rise_agg = rise[['Value', 'Time_diff']].agg({'Value': 'max', 'Time_diff': 'sum'})

    # timestamp is start point of the rise
    rise_agg['Timestamp'] = rise.iloc[0,:]['Timestamp']

    rise_agg['Value'] = rise_agg['Value'] - min(rise['Value'])

    rises_grouped.append(rise_agg)

rises_grouped = pd.DataFrame(pd.concat(rises_grouped, axis = 1)).transpose()

# need to convert to floating point because seaborn doesn't like pandas datetimes.
rises_grouped['Time_diff'] = (rises_grouped['Time_diff'] / np.timedelta64(1, 'm'))
rises_grouped['Value'] = rises_grouped['Value'].apply(np.float64)

rises_grouped = rises_grouped[rises_grouped.Value != 0.0]
rises_grouped = rises_grouped.rename(columns={'Value': 'Value_range', 'Time_diff': 'Time_diff'})

filtered_rises_grouped = rises_grouped.loc[(rises_grouped['Time_diff'] > 5) & (rises_grouped['Time_diff'] < 10) &
                                           (rises_grouped['Value_range'] > 25)]
print(filtered_rises_grouped)

measurePts = {'bw_rl_hzg': 5,
              'bw_vl_hzg': 12,
              'bw_rl_ww': 6,
              'bw_vl_ww': 7,
              'solar_vl': 8,
              'solar_rl': 9,
              'ww_mixed': 10,
              'ww_unmixed': 11
              }

fig, axs = plt.subplots(1, len(filtered_rises_grouped), sharex = False, sharey = True)

for n in range(len(filtered_rises_grouped)):

    # select 1 hr before and 1 hr after the start of the rise
    t0 = filtered_rises_grouped.iloc[n,:]['Timestamp']
    df_time_filter = df_all.loc[(df_all['Timestamp'] >= t0 - pd.Timedelta('1h')) & 
    (df_all['Timestamp'] <= t0 + pd.Timedelta('1h'))]

    for name in measurePts:
        measureID = measurePts[name]
        sysData = df_time_filter.loc[df_time_filter['MeasurementId'] == measureID]
        if 'bw' in name:
            line_style = 'solid'
        else:
            line_style = 'dashed'
        axs[n].plot(sysData['Timestamp'], sysData['Value'], label = name, linestyle = line_style)

    axs[n].set_title(str(t0.date()))    
    axs[n].plot(sysData['Timestamp'], sysData['TT_10'], label = 'temp_outside', linestyle = 'dotted')
    axs[n].xaxis.set_major_locator(dates.HourLocator())
    #axs[n].xaxis.set_major_locator(dates.AutoDateLocator(maxticks=3)) # sets x ticks
    axs[n].set_yticks(np.arange(10, 80, 5)) # sets y ticks

handles, labels = axs[-1].get_legend_handles_labels()
plt.figlegend(handles, labels, loc='lower center', ncol=len(handles)) # do NOT use loc = 'best'
fig.suptitle('BW VL HZG rise 5-10 min, at least 25 C')
axs[0].set_ylabel('Temperature (deg C)')
plt.show()