# this file reads the SigmaHeat heating system data and weather data from Deutsche Wetterdienst (DWD)
# then appends weather temp data to SigmaHeat data
# remember that different devices are located in different postcodes, i.e. different weather stations

from pandas import Series, DataFrame
import pandas as pd

# system and weather are the CSV file names where the data is stored
# feed to the function with string format
def mergeWeather(systemFile, weatherFile):

    system = (pd.read_csv(systemFile, parse_dates=[1])
            .reset_index(drop=True)
            )

    # create a new column on the data that rounds the boiler timestamps to the nearest 10 min
    #rounded_timestamps = DataFrame(boiler['Timestamp'].round('10min'), columns = ['Timestamp_10min'])
    #boiler = pd.concat([boiler, rounded_timestamps], axis=1)
    system['Timestamp_10min'] = system['Timestamp'].round('10min')

    # in the weather data, TT_10 is temp at 2 m high, and TM5_10 is at 5 cm high
    # the data has measurements at 10 min intervals (00:00, 00:10, 00:20...)
    # usecols and parse_dates don't play nice with each other,
    # so that's why we're getting the entire dataset first
    weather = pd.read_csv(weatherFile, delimiter=";", parse_dates=[1])

    # rename the columns for merging
    # inplace is so that you don't have to assign to a new variable
    weather.rename(columns={'MESS_DATUM': 'Timestamp_10min'}, inplace=True)

    # only take these two columns for the merge
    weather = weather[['Timestamp_10min', 'TT_10']]

    return pd.merge(system, weather, how='left', on='Timestamp_10min')