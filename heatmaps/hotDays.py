# looks at hot days and graphs the temps on that day

import pandas as pd
import os

# BW_VL_WW is condensing boiler feed pipe to warm water storage
solar_vl = pd.read_csv(os.path.join(
    'data', 'withWeather', 'solar_vl.csv'), parse_dates=['Timestamp'])

minTemps = 35
hour = 20

hotTemps = solar_vl.loc[(solar_vl['Value'] > minTemps) & (solar_vl['Timestamp'].dt.hour == hour)]

hotTemps['Date'] = hotTemps['Timestamp'].dt.date

hotDays = (hotTemps.drop_duplicates(subset=['Date'])
           .loc[:, 'Date']
           .reset_index(drop=True))

print(hotDays)
