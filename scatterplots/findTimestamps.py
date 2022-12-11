# finds timestamps where the value was more than 70 deg

import pandas as pd
import os

vl_hz = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_vl_hzg.csv'), parse_dates=['Timestamp'])[['Timestamp', 'Value', 'TT_10']]

vl_hz = vl_hz.rename(columns={'Value': 'VL_Hzg'})

high_vl_hz = vl_hz.loc[vl_hz['VL_Hzg'] >= 70]

vl_ww = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_vl_ww.csv'), parse_dates=['Timestamp'])[['Timestamp', 'Value']]

vl_ww = vl_ww.rename(columns={'Value': 'VL_WW'})

high_vl_hz = high_vl_hz.merge(vl_ww, on='Timestamp', how = 'left')

# reorder columns
high_vl_hz = high_vl_hz[['Timestamp', 'VL_Hzg', 'VL_WW', 'TT_10']]

# where the file will be saved
savePath = os.path.join('data', 'withWeather', 'bw_vl_hzg_over_70.csv')

high_vl_hz.to_csv(savePath)
print(high_vl_hz)