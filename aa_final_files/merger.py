# this file reads the SigmaHeat heating system data and weather data from Deutsche Wetterdienst (DWD)
# then appends weather temp data to SigmaHeat data
# remember that different devices are located in different postcodes, i.e. different weather stations

import pandas as pd

# system and weather are the CSV file names where the data is stored
# feed to the function with string format
def mergeWeather(systemFile, weatherFile):

    # read data 
    system = (pd.read_csv(systemFile, parse_dates=[1])
            .reset_index(drop=True)
            )

    # and round off to nearest second for consistency (because some data is hh:mm:ss, others hh:mm:ss.xxxx)
    system['Timestamp'] = system['Timestamp'].round('1s')

    # create a new column on the data that rounds the boiler timestamps to the nearest 10 min
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