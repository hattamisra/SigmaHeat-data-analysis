# Histograms of values at certain timestamps (e.g. 3 am)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# read csv, dates is in column 1, and reset the indexing
df = (pd.read_csv(os.path.join('data', 'withWeather', 'data_with_weather_2021-08-24.csv'),
                  parse_dates=[1])
      .reset_index(drop=True)
      )

# create a list of dataframes
sensor_names = ['Ruecklauf', 'Vorlauf']
sensors = []
for nPos in [0, 7]:
    sensors.append(df.loc[df['Position'] == nPos, ['Timestamp', 'Value']]
                   .reset_index(drop=True)
                   )

hour = 12

fig, axs = plt.subplots(nrows = 2, ncols = 1, sharex = True, sharey = True)
bins = np.arange(15, 55, 0.2)

# plot histograms at the hour
for n in [0, 1]:
    data = sensors[n].loc[sensors[n]['Timestamp'].dt.hour == hour, ['Value']]
    axs[n].hist(data, bins)
    axs[n].set_title('BW' + sensor_names[n])

plt.xticks(ticks = bins[::5])
plt.xlabel('Temperatures, degrees C')
fig.supylabel('Frequency')
fig.suptitle('Condensing boiler (BW) temperatures, hour ' + str(hour) + ', entire dataset')
plt.show()