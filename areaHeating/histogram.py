# Histograms of values at certain timestamps (e.g. 3 am)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# read csv, dates is in column 1, and reset the indexing
df = (pd.read_csv('floorHeat.csv', parse_dates=[1])
      .reset_index(drop=True)
      )

# create a list of dataframes for (Rue)cklauf, (Ra)umtemp, and (Vo)rlauf
sensor_names = ['Vorlauf', 'Raumtemp', 'Ruecklauf']
sensors = []
for nPos in range(3):
    sensors.append(df.loc[df['Position'] == nPos, ['Timestamp', 'Value']]
                   .reset_index(drop=True)
                   )

hour = 3

fig, axs = plt.subplots(nrows = 3, ncols = 1, sharex = True, sharey = True)
bins = np.arange(-5, 30, 0.2)

# plot histograms at the hour
for n in range(3):
    data = sensors[n].loc[sensors[n]['Timestamp'].dt.hour == hour, ['Value']]
    axs[n].hist(data, bins)
    axs[n].set_title(sensor_names[n])

plt.xticks(ticks = bins[::5])
plt.xlabel('Temperatures, degrees C')
fig.supylabel('Frequency')
fig.suptitle('Flächenhzg temperatures, hour ' + str(hour) + ', entire dataset')
plt.show()