import pandas as pd

df = pd.read_csv('export.csv')
floorHeat = (df.loc[df['DeviceId'] == 44324]
    .sort_values('Timestamp')
    .reset_index(drop=True)
)

floorHeat.to_csv('floorHeat.csv')