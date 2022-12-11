# from pandas import Series, DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import os

fileName1 = 'bw_vl_hzg.csv'
path1 = os.path.join('data','withWeather', fileName1)

fileName2 = 'bw_vl_ww.csv'
path2 = os.path.join('data','withWeather', fileName2)

# read csv
df1 = (pd.read_csv(path1, parse_dates=['Timestamp']))
df2 = (pd.read_csv(path2, parse_dates=['Timestamp']))

# select month and day
month = 5
# day = 21
# hr0 = 14
# hr1 = 16

df1 = (df1.loc[df1['Timestamp'].dt.month == month]
      #.loc[df1['Timestamp'].dt.day == day]
      #.loc[(df1['Timestamp'].dt.hour >= hr0) & (df1['Timestamp'].dt.hour < hr1)]
      .sort_values('Timestamp')
      .reset_index(drop=True)
      )

df2 =(df2.loc[df2['Timestamp'].dt.month == month]
      #.loc[df2['Timestamp'].dt.day == day]
      #.loc[(df2['Timestamp'].dt.hour >= hr0) & (df2['Timestamp'].dt.hour < hr1)]
      .sort_values('Timestamp')
      .reset_index(drop=True)
      )

dfPrint = df1

print(dfPrint)

# return, room temperature, feed
# ruecklauf is position 0, vorlauf is position 7

# plot
plt.plot(df1['Timestamp'], df1['Value'], label = fileName1)
#plt.plot(df2['Timestamp'], df2['Value'], label = fileName2)

plt.title(calendar.month_name[month])
#plt.title(calendar.month_name[month] + ' ' + str(day))
plt.legend()
plt.show()