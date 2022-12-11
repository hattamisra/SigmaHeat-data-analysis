# heatmap
# x axis is day of week (monday 0 to sunday 6)
# y axis is hour of day (00-23, so 00 represents 00:00-00:59)
# z axis (color map) is temperature (value from the file being read)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# create a dataframe by reading the appropriate file
# the example here is BW_VL_WW
df_sys = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_vl_ww.csv'), parse_dates=['Timestamp'])

# get columns that we need
df_sys = df_sys[['Timestamp', 'Value', 'TT_10']]

# add a column for day of the week
df_sys['Day of week'] = df_sys['Timestamp'].dt.day_of_week

# add a column for hour of day
df_sys['Hour of day'] = df_sys['Timestamp'].dt.hour

# median system temperatures for each hour, each day of the week (e.g. Tuesday 18:00:00 [to 18:59:59])
medianSys = df_sys.groupby(['Day of week', 'Hour of day']).agg(
    'median').reset_index().drop(columns='TT_10')

# now pivot to create a 2D array where the columns are days of the week, rows are each 1 hr block,
# and values are corresponding medians for that time and hour block
medianSys = medianSys.reset_index().pivot(index='Day of week', columns='Hour of day', values='Value')

sns.heatmap(medianSys, cmap = "rainbow").set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
plt.title('Median BW Vorlauf temperatures by hour and day, April-August')
plt.show()