# tempSpikes v4
# See documentation for more info.
# This file looks at BW VL WW temperatures 
# before and after BW VL WW peaks.
# This plots temperature relative to the peak value
# so if peak value = 50 and value at a certain period = 45,
# the data point for the box plot will be -5, because 45-50 = -5

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import datetime as dt
import math
import matplotlib.pyplot as plt
import os

# check runtime
begin_runtime = dt.datetime.now()

df = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_vl_hzg.csv'), parse_dates=['Timestamp'])

# start and end times for looking at max values (no padding)
t0_nopad = dt.time(hour=0, minute=30)
t1_nopad = dt.time(hour=23, minute=30)

# period; a string to feed into .floor method
# date can be changed to other periods (e.g. 15 min intervals, by .floor('15min'))
# 6min seems okay
period = '6min'

# start and end times, with padding
# e.g. if start time is 20:00 and we want to see 5 min before,
# the pad start would be 19:55
# need to convert to datetime for the + and - operations
pad = dt.timedelta(minutes = 5)

# step for the bins
step = pd.Timedelta('20s')

# how big the steps are for the x ticks - ideally shows every minute
# so if step is 10sec, set to 6
tickStep = 3

# threshold values
thresholdTemp = 65
thresholdDiffMin = 5
thresholdDiffMax = 100

# if skew_right is True, the plot will be [pad] after the peak
# otherwise, it will be [pad] before and after the peak
# set to False if we want to do local max instead of period changes
# (i.e. if thresholdDiff = 0)
skew_right = False

if skew_right == True:
    t0 = dt.datetime.combine(dt.date.min, t0_nopad)
    t1 = dt.datetime.combine(dt.date.min, t1_nopad) + pad
else:
    t0 = dt.datetime.combine(dt.date.min, t0_nopad) - pad
    t1 = dt.datetime.combine(dt.date.min, t1_nopad) + pad

# convert t0 and t1 back to time
t0 = t0.time()
t1 = t1.time()

# get the values we need
# set the index to timestamp for methods that require a DatetimeIndex
# but keep the timestamp column for references that require column
df = df[['Timestamp', 'Value']]  # .set_index('Timestamp', drop=False)

# get a column for dates with .floor('D')
df.insert(0, 'Period', pd.DatetimeIndex(df['Timestamp']).floor(period))

# create df without padding to look at maxima in periods between t0 and t1
df_nopad = df.loc[(df['Timestamp'].dt.time >= t0_nopad) &
                  (df['Timestamp'].dt.time < t1_nopad)]

df = df.loc[(df['Timestamp'].dt.time >= t0) & (df['Timestamp'].dt.time < t1)]

# sort out max temp values by period
# then find the indices of the max values and just keep that
maxTempsIdx = df_nopad.groupby('Period', as_index=False)[
    'Value'].idxmax()['Value']
maxTemps = df_nopad.loc[maxTempsIdx, :]

# ditto for minimum temperature values
# but rename columns in minTemps for merging
minTempsIdx = df_nopad.groupby('Period', as_index=False)[
    'Value'].idxmin()['Value']
minTemps = df_nopad.loc[minTempsIdx, :]

minTemps = minTemps.rename(
    {'Timestamp': 'Timestamp_min', 'Value': 'Value_min'}, axis=1)

# now merge maxTemps and minTemps
maxMinTemps = maxTemps.merge(minTemps, on=['Period'])

# then find the timestamps corresponding to the values
# only select rows with max values over thresholdTemp degrees
# (indicating hot/active system)
# and rows with min values at least thresholdDiff degrees less than max value
# (indicating temp spike, not just residual heat)
maxMinTemps = maxMinTemps.loc[(maxMinTemps['Value'] > thresholdTemp) &
                              (maxMinTemps['Value_min'] < maxMinTemps['Value'] - thresholdDiffMin) &
                              (maxMinTemps['Value_min'] > maxMinTemps['Value'] - thresholdDiffMax)]

# now slice the dataframe
# take data 5 min before and 5 min after timestamps of max temp
# there's a better way to write this than using a for loop,
# but for now let's just see how it goes

data_slice = []

## getting data around peaks

# tPeakTemp is time of peak for each period (on each row)
# note that peak of period != local maximum 
for tPeakTemp, peakValue in zip(maxMinTemps['Timestamp'], maxMinTemps['Value']):

    # take all measurements [pad] minutes before and after the peak value time
    if skew_right == True:
        around_peak = df.loc[(
            df['Timestamp'] >= tPeakTemp) & (df['Timestamp'] < tPeakTemp + pad)]
    else:
        around_peak = df.loc[(
            df['Timestamp'] >= tPeakTemp - pad) & (df['Timestamp'] < tPeakTemp + pad)]

    # if the value at tPeakTemp isn't the local maximum, ignore the period
    # this could happen if, for instance, the temp was increasing throughout the period
    # (so tPeakTemp is the last measurement in the period)
    if (skew_right == False) and (peakValue < max(around_peak['Value'])):
        pass
    else:
        # resample to ensure equal length of columns
        # take the mean, to deal with multiple values in the same bin
        around_peak_resampled = around_peak.resample(
            step, on='Timestamp', origin=tPeakTemp).mean()
        
        # turn DataFrame into Series, transpose
        around_peak_resampled = Series(around_peak_resampled['Value']).T

        # change the values to be the difference from the peak value
        # round to 2 decimal places to avoid float errors
        around_peak_resampled = round(around_peak_resampled - peakValue, 2)

        # change to list
        around_peak_resampled = around_peak_resampled.tolist()
        
        # append as item in list
        data_slice.append(around_peak_resampled)

# change to data frame
df_slice = DataFrame(data_slice)

# insert a column for the peak value 
# which will be 0 since the values are now differences from peak value
# if skewed right, it's going to be the first column. else, it's the midpoint.
if skew_right == True:
    df_slice.insert(0, 0, 0, allow_duplicates=True) # loc, column, value
else:
    df_slice.insert(math.trunc(len(df_slice.columns)/2), 0, 0, allow_duplicates=True)

# columns of the data frame
# the columns would be a list of seconds before/after peak
# for example: [-120, -90... 0, ... 90, 120]
pad_int = pad.seconds
if skew_right == True:
    slice_cols = np.linspace(0, pad_int, num=len(df_slice.columns))
else:
    slice_cols = np.linspace(-pad_int, pad_int, num=len(df_slice.columns))
df_slice.columns = slice_cols

print(df_slice)

## plotting

# filter out NaN values in each column because boxplot doesn't show if there is NaN
filtered_df_slice = df_slice.apply(lambda col: col.dropna().tolist())

fig, ax = plt.subplots()

ax.boxplot(filtered_df_slice, showfliers=False)  # do not show outliers
# ax.violinplot(filtered_df_slice) can also be used

ax.set_xticks(range(1, len(slice_cols) + 1, tickStep))

# set x ticks before this because matplotlib docs say to
ax.set_xticklabels(slice_cols[::tickStep])

if skew_right == True:
    ax.set_xlabel('Seconds after peak time')
else:
    ax.set_xlabel('Seconds before/after peak time')
ax.set_ylabel('Temperature difference from peak (degrees C)')
ax.set_title('Profiles of BW VL Hzg temperature spikes, at least ' + str(thresholdTemp) + ' deg C')

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()