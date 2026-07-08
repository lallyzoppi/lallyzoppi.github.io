import os
import xarray as xr
import numpy as np
import pandas as pd


BASE = "ERA5_extracted"

OUTPUT = "ERA5_DAILY_GRID.csv"


instant_files = []
accum_files = []


for root, dirs, files in os.walk(BASE):

    for f in files:

        if f.endswith("instant.nc"):
            instant_files.append(
                os.path.join(root,f)
            )

        if f.endswith("accum.nc"):
            accum_files.append(
                os.path.join(root,f)
            )


print("instant:",len(instant_files))
print("accum:",len(accum_files))


# wind + temperature

ds_inst = xr.open_mfdataset(
    sorted(instant_files),
    combine="by_coords"
)


# rain 

ds_tp = xr.open_mfdataset(
    sorted(accum_files),
    combine="by_coords"
)


ds = xr.merge(
[
ds_inst,
ds_tp[["tp"]]
]
)



# ==========================
# FEATURES
# ==========================

ds["wind_speed"] = np.sqrt(
    ds.u10**2 +
    ds.v10**2
)


# Kelvin -> Celsius

ds["t2m"] = (
    ds.t2m - 273.15
)


# metri -> mm

ds["tp"] = (
    ds.tp * 1000
)



# ==========================
# dataframe
# ==========================

df = (
    ds
    .to_dataframe()
    .reset_index()
)



df["date"] = pd.to_datetime(
    df["valid_time"]
)


df["year"] = (
    df.date.dt.year
)

df["month"] = (
    df.date.dt.month
)

df["day"] = (
    df.date.dt.day
)


df = df.drop(
columns=["valid_time"]
)



df.to_csv(
OUTPUT,
index=False
)


print("CREATO:")
print(OUTPUT)

print(df.head())

print(df.shape)
