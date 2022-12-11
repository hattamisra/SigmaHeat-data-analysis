# Makes a separate csv for every measurement point in the system
# merges data with weather data, stores the value in data/withWeather
# Reading a smaller csv enables the code to run quicker

import pandas as pd
import merger
import os

boilerFile = os.path.join('data', 'raw', 'condensingBoiler.2021-08-24.csv')
weatherFile = os.path.join(
    'data', 'raw', 'produkt_zehn_min_tu_20200224_20210826_04745.txt')

mergedData = merger.mergeWeather(boilerFile, weatherFile)

# drop unneeded columns
mergedData = mergedData.drop(columns=['Quantity', 'Digital', 'DeviceId']).reset_index(drop=True)

# where the file will be saved
savePath = os.path.join('data', 'withWeather')

# write csv where all points are there
mergedData.to_csv(os.path.join(savePath, 'data_with_weather_2021-08-24.csv'), index = False)

# system component names and the corresponding measurement IDs in a dictionary
# ww_mixed is WW Mischer, ww_unmixed is WW Speicher
# measurePts = {'bw_rl_hzg': 5,
#               'bw_vl_hzg': 12,
#               'bw_rl_ww': 6,
#               'bw_vl_ww': 7,
#               'solar_vl': 8,
#               'solar_rl': 9,
#               'ww_mixed': 10,
#               'ww_unmixed':11}

# go through each entry in the dictionary and write the csv to the path
# for name in measurePts:
#     # select the device being measured
#     sysComponent = mergedData.loc[mergedData['MeasurementId'] == measurePts[name]]
    
#     # write to csv
#     sysComponent.to_csv(os.path.join(savePath, name + '.csv'), index=False)