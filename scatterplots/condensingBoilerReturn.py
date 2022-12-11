# weatherTempExtractor
# this file reads the SigmaHeat heating system data and weather data from Deutsche Wetterdienst (DWD)
# then appends weather temp data to SigmaHeat data
# remember that different devices are located in different postcodes, i.e. different weather stations

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import merger

boilerFile = os.path.join('data', 'raw', 'condensingBoiler.2021-07.csv')
weatherFile = os.path.join('data', 'raw', 'produkt_zehn_min_tu_20200209_20210811_04745.txt')
hr = 20

merged = merger.mergeWeather(boilerFile, weatherFile)
minTemp = 10 # minimum temperature - 10 should give everything, 20-25 should give all else

# BW_RL_WW is condensing boiler return pipe to warm water storage
bw_rl_ww = (merged.loc[merged['MeasurementId'] == 6]
            .reset_index(drop=True)
            )

x = bw_rl_ww['TT_10'].loc[(bw_rl_ww['Timestamp'].dt.hour == hr) & (bw_rl_ww['Value'] > minTemp)]
y = bw_rl_ww['Value'].loc[(bw_rl_ww['Timestamp'].dt.hour == hr) & (bw_rl_ww['Value'] > minTemp)]

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 10})

ax.set(xlabel = 'Outside temperature', ylabel = 'System component temperature')

plt.title("Condensing boiler return from warm water storage, hour " + str(hr))
plt.show()