import xarray as xr
import pandas as pd
import numpy as np

measurements = pd.read_csv("data/measurements.csv", index_col="time", infer_datetime_format=True, parse_dates=["time"])
contaminations = pd.read_csv("data/contamination/contaminations.csv", infer_datetime_format=True).set_index(["time", "nano_id"])
# open figure

df = measurements \
    .reset_index() \
    .rename(columns={"id": "nano_id"}) \
    .set_index(["time", "nano_id"])

ds = xr.Dataset(df).unstack()

daph = xr.load_dataarray("data/measurements/daphnia_raw.nc")
cule = xr.load_dataarray("data/measurements/culex_raw.nc")
raw = daph.combine_first(cule).to_dataset(name="pixels")
raw["time"] = raw["time"].astype("datetime64")

esfenvalerate = xr.Dataset(contaminations).unstack()
esfenvalerate["time"] = esfenvalerate["time"].astype("datetime64")


data = raw.merge(ds)
data = data.merge(esfenvalerate)

data.to_netcdf("data/final_dataset.nc")