# Looks at periods where the temps are rising
# because that's when the boiler is operating

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import os

begin_runtime = dt.datetime.now()  # check runtime

# changeable parameters
fileName = 'bw_vl_hzg'  # name of file where we get the data (excl extension)

# filter out the noise (small fluctuations caused by measure errors)
minValueDiff = 0.05  # if value2 - value1 > minValueDiff

# filters out the periods without measurements
maxTimeDiff = pd.Timedelta('30s')  # if timestamp2 - timestamp1 < maxTimeDiff

# dayOfWeek = 1  # Monday = 0

hourStart = 12
hourEnd = 16

# creation of dataframe
path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value']]

# filtering by day of the week, by hour of the day, etc.
df = df.loc[(df['Timestamp'].dt.hour >= hourStart) &
            (df['Timestamp'].dt.hour < hourEnd)]

# Differences column
# Time_diff: length of time from prev measurement
# Value_diff: value difference from prev measurement
df[['Time_diff', 'Value_diff']] = df.diff()

# filtering out periods without measurement
df = df.loc[df['Time_diff'] < maxTimeDiff]

# group by each date and add the times to it
dailyTotals = pd.DataFrame()
dailyTotals['Rise']  = df.loc[df['Value_diff'] > minValueDiff].groupby(df['Timestamp'].dt.date)['Time_diff'].sum()
dailyTotals['Total'] = df.groupby(df['Timestamp'].dt.date)['Time_diff'].sum()
dailyTotals['Rise Ratio'] = dailyTotals['Rise'] / dailyTotals['Total']
print(dailyTotals)

# plotting

dailyTotals.boxplot(column = ['Rise Ratio'])
plt.title(fileName.upper().replace('_',' ') + ' daily ratios of boiler operation time to total monitored time')
plt.xlabel('')
plt.show()