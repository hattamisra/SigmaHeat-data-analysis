# compare solar insolations between nearby stations
# e.g. Soltau, Rotenburg

from geopy import distance
from functools import reduce
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# close stations with data for GS_10: Soltau 4745, Bremen 00691, Hannover 02014
closeStationFiles = ['produkt_zehn_min_sd_20200305_20210905_04745.txt', 'produkt_zehn_min_sd_20200305_20210905_00691.txt', 
'produkt_zehn_min_sd_20200305_20210905_02014.txt']

closeStations = [] # empty list

for file in closeStationFiles:

    # create dataframe by reading file and append to list of dataframes
    closeStation = pd.read_csv(os.path.join('data','raw', file), 
    parse_dates = ['MESS_DATUM'], na_values = -999, delimiter=";")

    closeStation = closeStation[['STATIONS_ID', 'MESS_DATUM', 'GS_10']] # get columns that we need

    closeStations.append(closeStation) # append to list of dataframes

# have soltau, rotenburg, and nienburg
insolation = reduce(lambda left, right: pd.merge(left, right, on='MESS_DATUM', how = 'left'), closeStations)

insolation = insolation.rename(columns={'GS_10_x': 'GS_10_Soltau', 'GS_10_y': 'GS_10_Bremen', 'GS_10': 'GS_10_Hannover'})

x1 = insolation['GS_10_Bremen']
x2 = insolation['GS_10_Hannover']
y = insolation['GS_10_Soltau']

# create a figure with two axes, and call regplot on each axes
fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True)
sns.scatterplot(x=x1, y=y, ax=ax1, sizes=1)
sns.scatterplot(x=x2, y=y, ax=ax2, sizes=1)

ax1.set(xlabel = 'Bremen insolation', ylabel = 'Soltau insolation')
ax1.set_xlim(0, 70)
ax1.set_ylim(0, 70)

ax2.set(xlabel = 'Hannover insolation', ylabel = 'Soltau insolation')
ax2.set_xlim(0, 70)
ax2.set_ylim(0, 70)

fig.suptitle('Solar insolation')
plt.show()