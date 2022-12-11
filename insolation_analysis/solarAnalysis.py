# solarAnalysis
# histogram of solar Rücklauf/Vorlauf but spot the sunny and non sunny days
# box-whisker for sunny vs non sunny too?
# DWD gives solar insolation - maybe use that?

import os
from numpy import datetime64, int64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import the data for system measurement and insolation
# make sure all the date columns are parsed as datetime, otherwise the merge screws up!
solar_vl = pd.read_csv(os.path.join('data','withWeather','solar_vl.csv'), parse_dates = ['Timestamp', 'Timestamp_10min'])
insolation = pd.read_csv(os.path.join('data','raw','produkt_zehn_min_sd_20200224_20210826_04745.txt'), 
    parse_dates = ['MESS_DATUM'], na_values = -999, delimiter=";")

# rename columns, only take necessary columns, then merge
insolation = insolation.rename(columns={'MESS_DATUM': 'Timestamp_10min'})
insolation = insolation[['Timestamp_10min', 'GS_10']]

solar_vl = pd.merge(solar_vl, insolation, how='left', on='Timestamp_10min')

print(solar_vl)
print(insolation)

hr = 12
minTemp = 0

# GS_10 is 10min sum of solar incoming radiation
x = solar_vl['GS_10'].loc[(solar_vl['Timestamp'].dt.hour == hr) & (solar_vl['Value'] > minTemp)]
y = solar_vl['Value'].loc[(solar_vl['Timestamp'].dt.hour == hr) & (solar_vl['Value'] > minTemp)]

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 10})

ax.set(xlabel = 'Solar insolation, $J/{cm}^{2}$', ylabel = 'System component temperature')

plt.title("Solar Vorlauf temperatures and solar insolation, hour " + str(hr) + ', all data')
plt.show()