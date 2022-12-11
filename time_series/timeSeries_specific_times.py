# correlates time in which things rise to the temperature difference in that rise
# looks at extreme values, e.g. BW VL HZG rise at least 15 min, at most 15 C
# plots timeseries of all those values
# ideally 3 or fewer

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from pandas.core.tools.datetimes import DatetimeScalar

minValueDiff = 0.05

maxTimeDiff = pd.Timedelta('30s')

# dataframe for all data
path_all = os.path.join('data', 'withWeather', 'data_with_weather_2021-08-24.csv')
df_all = pd.read_csv(path_all, parse_dates=['Timestamp'])

# creation of dataframe
df = df_all.loc[df_all['Name'] == 'BW VL Hzg'][['Timestamp', 'Value']]

print(df)

df[['Time_diff', 'Value_diff']] = df.diff()

measurePts = {'bw_rl_hzg': 5,
              'bw_vl_hzg': 12,
              'bw_rl_ww': 6,
              'bw_vl_ww': 7,
              'solar_vl': 8,
              'solar_rl': 9,
              'ww_mixed': 10,
              'ww_unmixed': 11
              }

times = [pd.to_datetime('2021-05-03 04:29:39'), pd.to_datetime('2021-05-05 06:29:31')]

fig, axs = plt.subplots(1, len(times), sharex = False, sharey = True)

for n in range(len(times)):

    # select 1 hr before and 1 hr after the start of the rise
    t0 = times[n]
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
    axs[n].xaxis.set_major_locator(dates.MinuteLocator(interval=10))
    axs[n].xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    axs[n].set_yticks(np.arange(10, 80, 5)) # sets y ticks

handles, labels = axs[-1].get_legend_handles_labels()
plt.figlegend(handles, labels, loc='lower center', ncol=len(handles)) # do NOT use loc = 'best'
fig.suptitle('BW VL Hzg peaks over 50 deg C, more than 600 s after WW peak')
axs[0].set_ylabel('Temperature (deg C)')
plt.show()