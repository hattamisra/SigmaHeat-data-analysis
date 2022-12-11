# this function uses the merger module

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import merger

boilerFile = os.path.join('data', 'raw', 'condensingBoiler.2021-07.csv')
weatherFile = os.path.join('data', 'raw', 'produkt_zehn_min_tu_20200209_20210811_04745.txt')
hr = 20

merged = merger.mergeWeather(boilerFile, weatherFile)
minTemp = 21 # minimum temperature - 10 should give everything, 20-25 should give all else

# BW_VL_WW is condensing boiler feed pipe to warm water storage
bw_vl_ww = merged.loc[merged['MeasurementId'] == 7].reset_index(drop=True)

x = bw_vl_ww['TT_10'].loc[(bw_vl_ww['Timestamp'].dt.hour == hr) & (bw_vl_ww['Value'] > minTemp)]
y = bw_vl_ww['Value'].loc[(bw_vl_ww['Timestamp'].dt.hour == hr) & (bw_vl_ww['Value'] > minTemp)]

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 10})

ax.set(xlabel = 'Outside temperature', ylabel = 'System component temperature')

plt.title("Condensing boiler feed to warm water storage, hour " + str(hr))
plt.show()