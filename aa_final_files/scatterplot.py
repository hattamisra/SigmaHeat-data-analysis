# creates a scatterplot

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

hr = 20
minTemp = 21 # minimum temperature - 10 should give everything, 20-25 should give all else

# BW_VL_WW is condensing boiler feed pipe to warm water storage
#bw_vl_ww = merged.loc[merged['Name'] == 'BW VL WW'].reset_index(drop=True)
fileName = 'bw_vl_ww'
df = pd.read_csv(os.path.join('data', 'withWeather',
                 fileName + '.csv'), parse_dates=['Timestamp'])

x = df['TT_10'].loc[(df['Timestamp'].dt.hour == hr) & (df['Value'] > minTemp)]
y = df['Value'].loc[(df['Timestamp'].dt.hour == hr) & (df['Value'] > minTemp)]

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 10})

ax.set(xlabel = 'Outside temperature', ylabel = 'System component temperature')

plt.title("Condensing boiler feed to warm water storage, hour " + str(hr))
plt.show()

# reads the SigmaHeat heating system data and weather data from Deutsche Wetterdienst (DWD)
# then appends weather temp data to SigmaHeat data
# remember that different devices are located in different postcodes, i.e. different weather stations