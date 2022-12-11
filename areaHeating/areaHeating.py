import pandas as pd
import matplotlib.pyplot as plt

# read csv, dates is in column 1, and reset the indexing
df = (pd.read_csv('floorHeat.csv', parse_dates=[1])
      .reset_index(drop=True)
      )

df = (df.loc[df['Timestamp'].dt.month == 6]
      .loc[df['Timestamp'].dt.day <= 3]
      .sort_values('Timestamp')
      .reset_index(drop=True)
      )

# return, room temperature, feed
var_names = ['Vorlauf', 'Raumtemp', 'Rücklauf']

# test
for posNumber, name in enumerate(var_names):
    sensor = df.loc[df['Position'] == posNumber]
    plt.plot(sensor['Timestamp'], sensor['Value'], label=name)

plt.legend()
plt.show()
