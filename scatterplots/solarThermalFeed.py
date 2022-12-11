# this function uses the merger module

from pandas import Series, DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import merger

merged = merger.mergeWeather('condensingBoiler.csv', 'produkt_zehn_min_tu_20200209_20210811_04745.txt')
hr = 0
minTemp = 0 # minimum temperature - 10 should give everything, 20-25 should give all else

# solarthermalfeed to warm water storage
solarFeed = merged.loc[merged['MeasurementId'] == 8].reset_index(drop=True)

x = solarFeed['TT_10'].loc[(solarFeed['Timestamp'].dt.hour == hr) & (solarFeed['Value'] > minTemp)]
y = solarFeed['Value'].loc[(solarFeed['Timestamp'].dt.hour == hr) & (solarFeed['Value'] > minTemp)]

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 10})

ax.set(xlabel = 'Outside temperature', ylabel = 'System component temperature')

plt.title("Solar thermal feed to warm water storage, hour " + str(hr))
plt.show()