import pandas as pd

df = pd.read_csv('export.2021-08-24.csv')
condBoiler = (df.loc[df['DeviceId'] == 44326]
    .sort_values('Timestamp')
    .reset_index(drop=True)
)

condBoiler.to_csv('condensingBoiler.2021-08-24.csv')