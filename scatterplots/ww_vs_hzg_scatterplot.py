
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime as dt

begin_runtime = dt.datetime.now()

vl_ww = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_vl_ww.csv'), parse_dates=['Timestamp'])[['Timestamp','Value']]

vl_ww = vl_ww.rename({'Value': 'VL_WW'}, axis = 1)

vl_hz = pd.read_csv(os.path.join(
    'data', 'withWeather', 'bw_vl_hzg.csv'), parse_dates=['Timestamp'])[['Timestamp','Value']]

vl_hz = vl_hz.rename({'Value': 'VL_HZ'}, axis = 1)

merged = pd.merge(vl_ww, vl_hz, how = 'inner', on = 'Timestamp')

print(merged)

x = merged['VL_WW']
y = merged['VL_HZ']

ax = sns.regplot(x=x, y=y, scatter_kws={"s": 1}, line_kws={"color": "red"})

ax.set(xlabel = 'VL WW (deg C)', ylabel = 'VL Hzg (deg C)')
ax.set_box_aspect(1)

plt.title("VL WW vs VL Hzg")

# check runtime
runtime = str(dt.datetime.now() - begin_runtime)
print('Run time: ' + runtime)

plt.show()