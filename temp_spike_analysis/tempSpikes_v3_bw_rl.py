# tempSpikes - version 3
# instead of checking for large temperature changes, 
# check for local maxima within the padded timeframes

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import os

# check runtime
begin_runtime = dt.datetime.now()

# start and end times for looking at max values (no padding)
t0_nopad = dt.time(hour=0, minute=30)
t1_nopad = dt.time(hour=23, minute=30)

# period; a string to feed into .floor method
# date can be changed to other periods (e.g. 15 min intervals, by .floor('15min'))
period = '6min'

# start and end times, with padding
# e.g. if start time is 20:00 and we want to see 5 min before,
# the pad start would be 19:55
# need to convert to datetime for the + and - operations
pad = dt.timedelta(minutes = 2)

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

# condensing boiler feed to warm water system
df = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_rl_ww.csv'), parse_dates=['Timestamp'])

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
thresholdTemp = 22
thresholdDiffMin = 0.3
thresholdDiffMax = 0.5
maxMinTemps = maxMinTemps.loc[(maxMinTemps['Value'] > thresholdTemp) &
                              (maxMinTemps['Value_min'] < maxMinTemps['Value'] - thresholdDiffMin) &
                              (maxMinTemps['Value_min'] > maxMinTemps['Value'] - thresholdDiffMax)]

# now slice the dataframe
# take data 5 min before and 5 min after timestamps of max temp
# there's a better way to write this than using a for loop,
# but for now let's just see how it goes

step = pd.Timedelta('10s')

data_slice = []

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
        
        # turn DataFrame into Series, transpose, then to list
        around_peak_resampled = Series(around_peak_resampled['Value']).T.tolist()

        # insert a column for the peak value
        # if skewed right, it's going to be the first column. else, it's the midpoint.
        if skew_right == True:
            around_peak_resampled.insert(0, peakValue)
        else:
            around_peak_resampled.insert(int(np.floor(len(around_peak_resampled)/2)), peakValue)

        # append as item in list
        data_slice.append(around_peak_resampled)

# change to data frame
df_slice = DataFrame(data_slice)

# we then need to insert a column for the peak value
# if skewed right, it's going to be the first column. else, it's the midpoint.
# if skew_right == True:
#     df_slice.insert(0, 'Max', maxMinTemps['Value'].reset_index(drop=True))
# else:
#     df_slice.insert(int(np.floor(len(df_slice.columns)/2)), 'Max',
#                     maxMinTemps['Value'].reset_index(drop=True))

# the columns would be a list of seconds before/after peak
# for example: [-120, -90... 0, ... 90, 120]
pad_int = pad.seconds
if skew_right == True:
    slice_cols = np.linspace(0, pad_int, num=len(df_slice.columns))
else:
    slice_cols = np.linspace(-pad_int, pad_int, num=len(df_slice.columns))
df_slice.columns = slice_cols

# filter out NaN values in each column because boxplot doesn't show if there is NaN
filtered_df_slice = df_slice.apply(lambda col: col.dropna().tolist())

fig, ax = plt.subplots()

ax.boxplot(filtered_df_slice)#, showfliers=False)  # do not show outliers
# ax.violinplot(filtered_df_slice) can also be used

# how big the steps are for the x ticks
tickStep = 6

ax.set_xticks(range(1, len(slice_cols) + 1, tickStep))

# set x ticks before this because matplotlib docs say to
ax.set_xticklabels(slice_cols[::tickStep])

if skew_right == True:
    ax.set_xlabel('Seconds after peak time')
else:
    ax.set_xlabel('Seconds before/after peak time')
ax.set_ylabel('Temperature (degrees C)')
ax.set_title('Profiles of BW RL WW temperature spikes, ' +
             t0_nopad.strftime('%H:%M') + ' to ' + t1_nopad.strftime('%H:%M'))

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()