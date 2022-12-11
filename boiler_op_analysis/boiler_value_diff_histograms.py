# Creates a histogram of all positive temperature differences
# The idea is to see where peaks are

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import os

begin_runtime = dt.datetime.now()  # check runtime

## changeable parameters

fileName = 'bw_vl_hzg' # name of file where we get the data (excl extension)

# filter out the noise (small fluctuations caused by measure errors)
minValueDiff = -50 # if value2 - value1 > minValueDiff

# filters out the periods without measurements
maxTimeDiff = pd.Timedelta('30s') # if timestamp2 - timestamp1 < maxTimeDiff

## creation of dataframe

path = os.path.join('data', 'withWeather', fileName + '.csv')
df = pd.read_csv(path, parse_dates=['Timestamp'])[['Timestamp', 'Value']]

# create boolean column in the dataframe
# True if the value increased more than minValueDiff compared to previous value
df[['Time_diff', 'Value_diff']] = df.diff()

## filtering out data

df = df.loc[(df['Value_diff'] > minValueDiff)
            & (df['Time_diff'] < maxTimeDiff)]

histBins = np.arange(0.1, 2, 0.1)-0.05#.round(1)

plt.hist(df['Value_diff'], bins = histBins, align = 'mid')
plt.xticks(histBins[::10] + 0.05)
plt.xlabel('Temperature difference from previous (degrees C)')
plt.ylabel('Frequency')
plt.title('Histogram of temperature differences, 0.1 degree C bins, ' + fileName)
plt.show()