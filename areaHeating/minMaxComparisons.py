from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy

# read csv, dates is in column 1, and reset the indexing
df = (pd.read_csv('floorHeat.csv', parse_dates=[1])
      .reset_index(drop=True)
      )

# look in June
df = (df.loc[df['Timestamp'].dt.month == 6]
      .sort_values('Timestamp')
      .reset_index(drop=True)
      )

# create a list of dataframes for (Rue)cklauf, (Ra)umtemp, and (Vo)rlauf
sensor_names = ['Vorlauf', 'Raumtemp', 'Rücklauf']
sensors = []
for nPos in range(3):
    sensors.append(df.loc[df['Position'] == nPos, ['Timestamp', 'Value']]
                   .reset_index(drop=True)
                   )

minimums = []
maximums = []

# face and edge colors for plotting. 1 at the end means it's fully opaque
face_colors = [[1, 0, 0, 0.2], [0, 1, 0, 0.2], [0, 0, 1, 0.2]]
edge_colors = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]

fig, ax = plt.subplots()

# get minimum values
for n, sensor in enumerate(sensors):

    # create new columns for hours and minutes
    sensor.insert(1, 'HHMM', sensor['Timestamp'].dt.strftime('%H:%M'))

    minimums.append(sensor.groupby('HHMM', as_index=False)
        .aggregate({'HHMM': 'first', 'Value': 'min'})
    )

    maximums.append(sensor.groupby('HHMM', as_index=False)
        .aggregate({'HHMM': 'first', 'Value': 'max'})
    ) 
    
    # plot shaded regions between the max and min lines with some transparency
    # minimums[n] gets the nth DataFrame in the list. Then ['HHMM'] gets the column.
    ax.fill_between(minimums[n]['HHMM'], maximums[n]['Value'], minimums[n]['Value'], 
        label = sensor_names[n], facecolor = face_colors[n], edgecolor = edge_colors[n]
    )

# ticks every 60 minutes
plt.xticks(ticks = minimums[0]['HHMM'].iloc[::60], labels = minimums[0]['HHMM'].iloc[::60])
plt.title('Flächenhzg min/max temperatures, June')
ax.legend(loc = 'lower right')
plt.show()