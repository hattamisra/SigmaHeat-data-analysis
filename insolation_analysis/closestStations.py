# compare solar insolations between nearby stations
# e.g. Soltau, Rotenburg

from geopy import distance
from functools import reduce
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

path = os.path.join('data', 'raw', 'zehn_min_sd_Beschreibung_Stationen.txt')

stations = pd.read_fwf(path, encoding='mac_roman',
                       sep=None, skiprows=[0], IndexCol=0, header=None)

columnNames = {0: 'Stations_id', 1: 'von_datum', 2: 'bis_datum', 3: 'Stationshoehe',
               4: 'geoBreite', 5: 'geoLaenge', 6: 'Stationsname', 7: 'Bundesland'}

stations = stations.rename(columns=columnNames)

# location of Jan's parents' house, as a tuple
parentsHouse = (52.9787645, 9.5860159)

# convert Soltau lat/long to tuples
soltau = stations.loc[stations.Stations_id == 4745, stations.columns[4:6]]
soltau = (float(soltau['geoBreite']), float(soltau['geoLaenge']))

# distance.distance requires two tuples, each in format (latitude, longitude) as input
stations['Distance to parents (km)'] = stations.apply(lambda df: distance.distance(
    (df['geoBreite'], df['geoLaenge']), parentsHouse).km, axis=1)

stations['Distance to Soltau (km)'] = stations.apply(lambda df: distance.distance(
    (df['geoBreite'], df['geoLaenge']), soltau).km, axis=1)

# closest stations to parents house with GS_10 data: soltau 04745, bremen 00691, hannover 02014
print(stations.nsmallest(5, 'Distance to parents (km)'))
