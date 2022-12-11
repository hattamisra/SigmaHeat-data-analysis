# tempSpikes - version 5
# check for local maxima within the padded timeframes
# and use the relative temperature differences to the max
# and compare RL temperatures to before/after VL peaks

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import datetime as dt
import math
import matplotlib.pyplot as plt
import os

# check runtime
begin_runtime = dt.datetime.now()

VL_file = 'bw_vl_ww'
df = pd.read_csv(os.path.join(
    'data', 'withWeather', VL_file + '.csv'), parse_dates=['Timestamp'])
RL_file = 'bw_rl_ww'
df['Value_RL'] = pd.read_csv(os.path.join(
    'data', 'withWeather', RL_file + '.csv'), parse_dates=['Timestamp'])['Value']

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
pad = dt.timedelta(minutes = 10)

# step for the bins
step = pd.Timedelta('20s')

# how big the steps are for the x ticks - ideally shows every minute
# so if step is 10sec, set to 6
tickStep = 3

# threshold values
thresholdTemp = 30
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
df = df[['Timestamp', 'Value', 'Value_RL']]  # .set_index('Timestamp', drop=False)

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
minTempsIdx = df_nopad.groupby('Period', as_index=False)[
    'Value'].idxmin()['Value']
minTemps = df_nopad.loc[minTempsIdx, :]

minTemps = minTemps.rename(
    {'Timestamp': 'Timestamp_min', 'Value': 'Value_min', 'Value_RL': 'Value_RL_min'}, axis=1)

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
for index, row in maxMinTemps.iterrows():

    tPeakTemp = row['Timestamp']
    peakVL = row['Value']

    # take all measurements [pad] minutes before and after the peak value time
    if skew_right == True:
        around_peak = df.loc[(
            df['Timestamp'] >= tPeakTemp) & (df['Timestamp'] < tPeakTemp + pad)]
    else:
        around_peak = df.loc[(
            df['Timestamp'] >= tPeakTemp - pad) & (df['Timestamp'] < tPeakTemp + pad)]

    peakRL = max(around_peak['Value_RL'])

    # if the value at tPeakTemp isn't the local maximum, ignore the period
    # this could happen if, for instance, the temp was increasing throughout the period
    # (so tPeakTemp is the last measurement in the period)
    if not( (skew_right == False) and ( peakVL < max(around_peak['Value']) ) ):

        # resample to ensure equal length of columns
        # take the mean, to deal with multiple values in the same bin
        ar_peak_resampled = around_peak.resample(
            step, on='Timestamp', origin=tPeakTemp).agg({'Value_RL': 'mean'})
        
        # turn DataFrame into Series, transpose
        ar_peak_resampled = Series(ar_peak_resampled['Value_RL']).T

        # change the values to be the difference from the peak RL value
        # round to 2 decimal places to avoid float errors
        ar_peak_resampled = round(ar_peak_resampled - max(ar_peak_resampled), 2)

        # change to list
        ar_peak_resampled = ar_peak_resampled.tolist()

        # insert, to the resampled list, the value of RL at VL peak
        # if skewed right, it's going to be the first column. else, it's the midpoint.
        rl_when_vl_peak = df.loc[df['Timestamp'] == tPeakTemp]['Value_RL']
        if skew_right == True:
            ar_peak_resampled.insert(0, rl_when_vl_peak - peakRL) # index, element
        else:
            ar_peak_resampled.insert(math.trunc(len(ar_peak_resampled)/2), rl_when_vl_peak - peakRL)
        
        # append as item in list
        data_slice.append(ar_peak_resampled)

# change to data frame with float items
df_slice = DataFrame(data_slice).astype('float')

# columns of the data frame
# the columns would be a list of seconds before/after peak
# for example: [-120, -90... 0, ... 90, 120]
pad_int = pad.seconds
if skew_right == True:
    slice_cols = np.linspace(0, pad_int, num=len(df_slice.columns))
else:
    slice_cols = np.linspace(-pad_int, pad_int, num=len(df_slice.columns))
df_slice.columns = slice_cols

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
    ax.set_xlabel('Seconds after VL WW peak time')
    ax.set_title(RL_file.upper().replace('_', ' ') + ' temp profiles after VL WW peaks, ' +
             t0_nopad.strftime('%H:%M') + ' to ' + t1_nopad.strftime('%H:%M'))
else:
    ax.set_xlabel('Seconds before/after VL WW peak time')
    ax.set_title(RL_file.upper().replace('_', ' ') + ' temp profiles before/after VL WW peaks, ' +
             t0_nopad.strftime('%H:%M') + ' to ' + t1_nopad.strftime('%H:%M'))
ax.set_ylabel('RL WW relative temperatures (degrees C)')

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()